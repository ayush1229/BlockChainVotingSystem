from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session as flask_session, make_response, current_user, abort
from flask_login import login_required, logout_user
from .. import web3_utils # Assuming web3_utils is in the parent directory of app
from app import bcrypt # Import bcrypt
from app.user.utils import save_picture # Import save_picture
from app.models import db, VotingSession, Candidate, Admin, User, ManualVerificationRequest # Import db and models and ManualVerificationRequest
import os
from datetime import datetime, timedelta # Import datetime and timedelta

main = Blueprint('main', __name__)

@main.route('/')

@main.route('/index')
def index():
    return render_template('index.html', title='Home')

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/candidates/<int:session_id>')
def candidates(session_id):
    session = VotingSession.query.get(session_id)
    if not session:
        abort(404) # Or redirect to an error page
    session = VotingSession.query.get(session_id)
    candidates = []
    if session:
        candidates = Candidate.query.filter_by(session_id=session_id).all()
    return render_template('candidates.html', title='Candidates', candidates=candidates)

@main.route('/importance')
def importance():
    return render_template('importance.html', title='Importance of Voting')


@main.route('/voter', methods=['GET', 'POST'])
def voter():
    # Need to determine the session ID for the voter to vote in.
    # This could come from a URL parameter, user's session, or by finding the active session.
    # Example: @main.route('/voter/<int:session_id>', methods=['GET', 'POST'])
    if request.method == 'POST':
        session_id = 1 # Placeholder: Replace with logic to get the actual session ID
        voter_address = "0x..."  # Placeholder voter address
        voter_private_key = "..."  # Placeholder voter private key (Handle securely in a real app)

        # Get the candidate index map from the database
        candidates = Candidate.query.filter_by(session_id=session_id).all()
        candidate_index_map = {candidate.name: i for i, candidate in enumerate(candidates)}

        voter_id = request.form.get('voterId')
        candidate = request.form.get('candidate')
        print(f"Vote submitted by Voter ID: {voter_id} for Candidate: {candidate}")
        # Add actual logic to interact with web3_utils.py for voting
        return redirect(url_for('main.submission'))

    return render_template('voter.html', title='Voter')

@main.route('/voter/<int:session_id>', methods=['GET', 'POST'])
def voter_with_id(session_id):
    if request.method == 'POST':
        selected_candidate_name = request.form.get('candidate')

        # TODO: Implement client-side Metamask interaction to get voter's wallet address
        # and potentially sign the transaction.
        voter_address = current_user.wallet_address if current_user.is_authenticated else None  # Get from linked wallet
        if not voter_address:
            flash('Please link your wallet to vote.', 'warning')
            return redirect(url_for('user.link_wallet'))  # Redirect to link wallet page

        # Placeholder for voter's private key (This should NOT be handled on the server in a real app)
        voter_private_key = os.getenv("PRIVATE_KEY")  # This is just for demonstration - very insecure!

        # Rest of the POST logic as above, using the session_id parameter
    return render_template('voter.html', title='Voter', session_id=session_id)

@main.route('/admin', methods=['GET', 'POST'])
def admin():
    from flask_login import login_user
    if request.method == 'POST':
        username = request.form.get('adminId')
        password = request.form.get('adminPassword')
        admin = Admin.query.filter_by(username=username).first()
        if admin and bcrypt.check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('main.admin_dashboard'))  # Redirect on success
        flash('Invalid Admin ID or Password', 'danger')
    return render_template('admin.html', title='Admin Login')

@main.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if request.method == 'POST': # This block is for handling POST requests to update settings
        verification_method = request.form.get('email_verification_method')
        allowed_domain = request.form.get('allowed_email_domain')
        manual_timelimit = request.form.get('manual_verification_timelimit', type=int)
        required_info = request.form.get('required_additional_info')

        current_user.email_verification_method = verification_method
        current_user.allowed_email_domain = allowed_domain if verification_method == 'institute' else None
        current_user.manual_verification_timelimit = manual_timelimit if verification_method == 'manual' else None
        current_user.required_additional_info = required_info if verification_method == 'manual' else None
        db.session.commit()
        flash('Email verification settings updated successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))

    # This part is for handling GET requests to display the dashboard
    pending_verification_requests = ManualVerificationRequest.query.filter_by(status='pending').all()
    return render_template('admin-dashboard.html', title='Admin Dashboard', pending_requests=pending_verification_requests)

@main.route('/admin/verify_request/<int:request_id>/<string:action>', methods=['GET'])
@login_required
def verify_request(request_id, action):
    verification_request = ManualVerificationRequest.query.get_or_404(request_id)

    if action == 'approve':
        verification_request.status = 'approved'
        # Call placeholder function to mint NFT
        # TODO: Implement web3_utils.mint_nft to interact with your smart contract
        # You'll need the user's wallet address and the session ID
        try:
            web3_utils.mint_nft(verification_request.user.wallet_address, verification_request.voting_session_id)
            flash('Verification request approved and NFT minted!', 'success')
        except Exception as e:
            flash(f'Error minting NFT: {e}', 'danger')

    elif action == 'reject':
        verification_request.status = 'rejected'
        flash('Verification request rejected.', 'info')

    db.session.commit()
    return redirect(url_for('main.admin_dashboard'))

@main.route('/create-voting-session', methods=['GET', 'POST'])
@login_required
def create_voting_session():
    if request.method == 'POST':
        # Placeholder for handling session creation
        title = request.form.get('title', 'New Voting Session') # Assuming a title field is added to the form
        start_time_str = request.form.get('start_time') # Use underscore to match form field name
        end_time_str = request.form.get('end_time') # Use underscore to match form field name

        # Parse start and end times (assuming datetime-local format: YYYY-MM-DDTHH:MM)
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
            duration_in_seconds = int((end_time - start_time).total_seconds())
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return render_template('create-voting-session.html', title='Create Voting Session')

        # Create a new voting session in the database
        candidate_names = []

        data_dir = os.path.join(current_app.root_path, '..', 'data', 'sessions')
        os.makedirs(data_dir, exist_ok=True)

        # Assuming the form sends candidate names and files with names like 'candidate-name-0', 'profile-pic-0', etc.
        candidate_data_list = []
        i = 0
        while True:
            candidate_name = request.form.get(f'candidate-name-{i}')
            profile_pic = request.files.get(f'profile-pic-{i}')
            if not candidate_name:
                break
            if profile_pic:
                filename = save_picture(profile_pic) # Use the save_picture function
                candidate_data_list.append({'name': candidate_name, 'image_file': filename})
            else:
                # Handle cases where no profile picture is uploaded
                candidate_data_list.append({'name': candidate_name, 'image_file': None}) # Or a default image filename
            candidate_names.append(candidate_name)
            i += 1
        
        new_session = VotingSession(
            title=title,
            start_time=start_time,
            end_time=end_time,
            is_active=True, # Set to active upon creation
            results_released=False,
            creator=current_user # Associate with the logged-in admin
        )
        db.session.add(new_session)
        db.session.commit() # Commit to get the session ID

        # Add candidates to the database
        for candidate_data in candidate_data_list:
            candidate = Candidate(name=candidate_data['name'], image_file=candidate_data['image_file'], session_id=new_session.id)
            db.session.add(candidate)
        db.session.commit()

        try:
            web3_utils.create_session("New Voting Session", candidate_names, duration_in_seconds)
            flash('Voting session created successfully!', 'success')
        except Exception as e:
            flash(f'Error creating voting session: {e}', 'danger')
        return redirect(url_for('main.admin_dashboard')) # Redirect after creation
    return render_template('create-voting-session.html', title='Create Voting Session')

@main.route('/release-results', methods=['GET', 'POST'])
@login_required
def release_results():
    session_id = request.args.get('session_id', type=int) # Get session_id from query parameter
    voting_session = VotingSession.query.get(session_id)
    if not voting_session or voting_session.admin_id != current_user.id:
        abort(403) # Forbidden
    if request.method == 'POST':
        try:
            web3_utils.release_results(session_id)
            flash('Voting results released successfully!', 'success')
        except Exception as e:
            flash(f'Error releasing results: {e}', 'danger')
        return redirect(url_for('main.admin_dashboard')) # Redirect after release
    return render_template('release-results.html', title='Release Results')

@main.route('/view-results/<int:session_id>')
@login_required
def view_results(session_id):
    voting_session = VotingSession.query.get(session_id)
    if not voting_session or voting_session.admin_id != current_user.id:
        abort(403) # Forbidden
    # Get candidates from the database
    candidates = Candidate.query.filter_by(session_id=session_id).all()

    # Get vote counts from the blockchain (adjust based on your web3_utils.get_candidates return format)
    # This assumes get_candidates returns a list of vote counts in the same order as candidates from the database.
    blockchain_results = web3_utils.get_candidates(session_id)
    combined_results = []
    # Assuming blockchain_results is a list of vote counts corresponding to the order of candidates in the database query
    for i, candidate in enumerate(candidates):
        # Find the corresponding vote count from blockchain_results based on candidate name or index
        # You might need more sophisticated logic here if the order or structure differs
        combined_results.append({'name': candidate.name, 'image_file': candidate.image_file, 'votes': blockchain_results[i] if i < len(blockchain_results) else 0})
    return render_template('view-results.html', title='View Results', results=combined_results)

@main.route('/submission')
def submission():
    return render_template('submission.html', title='Vote Submitted')

@main.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('main.admin'))