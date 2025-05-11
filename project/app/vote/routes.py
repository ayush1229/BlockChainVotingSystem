from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, logout_user # Import logout_user if needed in vote blueprint
from app import db
from sqlalchemy.orm import joinedload # Import joinedload
from app.models import VotingSession, Admin, UserSessionVerification, User, ManualVerificationRequest
import json

vote = Blueprint('vote', __name__)

@vote.route('/vote/<int:session_id>', methods=['GET', 'POST'])
@login_required
def vote_in_session(session_id):
    session = VotingSession.query.options(joinedload(VotingSession.candidates)).get_or_404(session_id) # Fetch candidates
    admin = Admin.query.get(session.admin_id)

    # Check if user is already verified for this session
    user_verification = UserSessionVerification.query.filter_by(
        user_id=current_user.id,
        voting_session_id=session_id
    ).first()
    
    # Find if there is a pending manual verification request
    pending_request = ManualVerificationRequest.query.filter_by(
        user_id=current_user.id,
        voting_session_id=session_id,
        status='pending'
    ).first()

    is_verified = user_verification and user_verification.is_verified
    if request.method == 'POST':
        if not is_verified and admin.email_verification_method is not None:
            # Implement logic to handle verification based on admin settings
            if admin.email_verification_method == 'manual':
                if not pending_request:
                    return redirect(url_for('vote.request_manual_verification', session_id=session_id)) # Redirect to manual verification request page
                else:
                     flash('Your manual verification request is pending review.', 'info')
            elif admin.email_verification_method == 'institute':
                # Check if any of the user's emails match the institute domain
                user_emails = json.loads(current_user.emails) if current_user.emails else []
                domain_matches = any(admin.allowed_email_domain in email for email in user_emails)

                if domain_matches:
                    # Mark user as verified for this session
                    if not user_verification:
                        user_verification = UserSessionVerification(user_id=current_user.id, voting_session_id=session_id, is_verified=True)
                        db.session.add(user_verification)
                    else:
                        user_verification.is_verified = True
                    db.session.commit()
                    is_verified = True # Update status after verification
                    flash('Email verified successfully. You can now vote.', 'success')
                else:
 flash(f'Voting in this session requires an email from the {admin.allowed_email_domain} domain.', 'danger')
 # Redirect back to the voting page with an error, or a dedicated info page
                return redirect(url_for('vote.vote_in_session', session_id=session_id))


        if is_verified:
            # Retrieve the selected candidate's ID from the form
            selected_candidate_id = request.form.get('candidate', type=int)

            # Map the candidate ID to the smart contract's index
            selected_candidate_index = -1
            for index, candidate in enumerate(session.candidates):
                if candidate.id == selected_candidate_id:
                    selected_candidate_index = index
                    break
            # This is a placeholder and highly insecure for production
            user_private_key = "YOUR_PRIVATE_KEY" # Replace with secure key management
            try:
                # Call web3_utils to interact with the smart contract
                # You will need to ensure web3_utils.vote handles NFT check internally
                web3_utils.vote(session_id, selected_candidate_index, current_user.wallet_address, user_private_key)
                flash('Your vote has been cast successfully!', 'success')
                return redirect(url_for('main.submission')) # Redirect to a success page
            except Exception as e:
                flash(f'Error casting vote: {e}', 'danger')
                return redirect(url_for('main.index')) # Redirect to an error page or back to vote page
        else:
            # This will only be reached if verification is required but not met
            flash('You need to complete the verification process to vote in this session.', 'danger')
            # Depending on the verification method, you might redirect to the appropriate page
            if admin.email_verification_method == 'manual' and not pending_request:
                 return redirect(url_for('vote.request_manual_verification', session_id=session_id))
            return redirect(url_for('vote.vote_in_session', session_id=session_id)) # Redirect back to vote page to show message

    # GET request: Display the voting page and verification status.
    return render_template('voter.html', title=session.title, session=session, is_verified=is_verified, admin=admin)

# Placeholder route for manual verification request submission
@vote.route('/vote/request_manual_verification/<int:session_id>', methods=['GET', 'POST'])
@login_required
def request_manual_verification(session_id):
    session = VotingSession.query.get_or_404(session_id)
    admin = Admin.query.get(session.admin_id)
    required_additional_info = admin.required_additional_info if admin else ""
    # Check if manual verification is indeed required for this session
    if admin.email_verification_method != 'manual':
        flash('Manual verification is not required for this session.', 'warning')
        return redirect(url_for('vote.vote_in_session', session_id=session_id))

    # Check if a request is already pending
    existing_request = ManualVerificationRequest.query.filter_by(
        user_id=current_user.id,
        voting_session_id=session_id
    ).first()

    if existing_request and existing_request.status == 'pending':
        flash('Your verification request is already pending review.', 'info')
        return redirect(url_for('vote.vote_in_session', session_id=session_id))
    elif existing_request and existing_request.status == 'approved':
        flash('You are already verified for this session.', 'success')
        return redirect(url_for('vote.vote_in_session', session_id=session_id))

    if request.method == 'POST':
        additional_info = request.form.get('additional_info') # Assuming a form field for additional info
        new_request = ManualVerificationRequest(
            user_id=current_user.id,
            voting_session_id=session_id,
 additional_info=additional_info # Changed from request.form.get('additional_info') to additional_info
        )

        db.session.add(new_request)
        db.session.commit()

        flash('Your verification request has been submitted for review.', 'success')
        return redirect(url_for('vote.vote_in_session', session_id=session_id))

    return render_template('request_manual_verification.html', title='Manual Verification Request', session=session, admin=admin)