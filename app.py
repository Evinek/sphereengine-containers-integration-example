import os
import logging
from dotenv import load_dotenv
from seco_api import SECOApi
from flask import Flask, jsonify, render_template

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# In production environment store lessons and workspaces in e.g. database
lessons = {
    'efa23f82-c074-4622-8f05-72fe2f7e573a': {
        'lesson_name': 'Python - first lesson',
        'project_id': 'e14be00ff57b4b889d7f163780aeacd6', # Console Python
    },
    'faace2f9-1c39-4f82-806d-7e33fd148cfe': {
        'lesson_name': 'C++ - first lesson',
        'project_id': '57510a395d2b4ec5a01fa7557a26a76f', # Console C++ (GCC 11.2)
    }
}

# {lesson_id: {user_id: workspace_id}}
workspaces: dict[str, dict[int, int]] = {
    lesson_id: {} for lesson_id in lessons
}


app.logger.debug('ENVS:')
for key, val in os.environ.items():
    if key.startswith('SECO_'):
        app.logger.debug(f'{key}: {val}')

@app.context_processor
def global_context():
    return {'SECO_URL': os.environ.get('SECO_URL')}

@app.route('/', endpoint="index")
def main():
    """
    List of lessons
    """
    return render_template('lessons.html', lessons=lessons)

@app.route('/lessons/<lesson_id>', endpoint='lesson')
def main(lesson_id):
    """
    Lesson with a workspace
    """
    if lesson_id not in lessons:
        return f'Lesson {lesson_id} not found', 404

    return render_template('lesson.html', lesson_id=lesson_id, lesson=lessons[lesson_id])


@app.route("/lesson/<lesson_id>/workspace", methods=['POST'], endpoint='lesson_workspace')
def get_workspace(lesson_id):
    """
    Returns the workspace data for the user.
    """

    # Verify if the user is logged in.
    if not is_logged_in():
        return jsonify({'error': 'You are not logged'}), 401
    
    # Invalid lesson...
    if lesson_id not in lessons:
        return jsonify({'error': f'Lesson {lesson_id} not found'}), 404
    
    user_id: int = get_user_id()
    lesson_workspaces = workspaces[lesson_id]
    workspace = None # the workspace to be displayed

    # Verify if the user used any workspace in the lesson already
    if user_id in lesson_workspaces:
        # We found the recently used workspace identifier.
        last_workspace_id: str = lesson_workspaces[user_id]
        app.logger.debug(f'The user has already used the workspace (ID: {last_workspace_id})')
        try:
            # Receive the workspace data.
            response = SECOApi.get_workspace(last_workspace_id)
            app.logger.debug(f'GET /workspaces/{last_workspace_id} output: {response}')

            workspace_state = response['state']['code']
            app.logger.debug(f"The workspace state: {response['state']['name']}")

            # Verify if the workspace is running.

            if workspace_state in (SECOApi.WORKSPACE_STATE_STARTING, SECOApi.WORKSPACE_STATE_RUNNING):
                # If the workspace is starting, we can show the workspace.
                # Prepare data to return
                workspace = {
                    'id': last_workspace_id,
                    'workspace_token': response['workspace_token'],
                }
            elif workspace_state == SECOApi.WORKSPACE_STATE_STOPPED:
                # When `auto_resume` was set as true we can display the workspace and it will be resumed automaticly.
                # Prepare data to return
                workspace = {
                    'id': last_workspace_id,
                    'workspace_token': response['workspace_token'],
                }

                # Here, you can manually resume the workspace if you have set the `auto_resume` flag to false.
                # In some cases, you must wait before the workspace can be resumed (e.g. when the workspace is being stopped), 
                # Therefore, your frontend should continue making requests until the workspace is running.
                
                # try:
                #     SECOApi.resume_workspace(last_workspace_id)
                #     workspace = {
                #         'id': last_workspace_id,
                #         'workspace_token': response['workspace_token'],
                #     }
                # except SECOApi.APIError as e:
                #     app.logger.debug(e)
                #     return jsonify({'error': "couldn't resume the workspace"}), 422

            # In case of the STARTING state, instead of displaying the workspace, 
            # you can show your custom loading screen and 
            # poll the backend until the workspace is running (reaching the RUNNING state).
            # After the workspace loaded, you can render the workspace.

        except SECOApi.APIError as e:
            app.logger.debug(e)
            return jsonify({'error': "couldn't get the workspace"}), 422

    # If the user has not assigned a workspace or if the workspace is not running
    if not workspace:
        app.logger.debug('Create a workspace for the user')
        try:
            # Get the project id for the current lesson.
            project_id = lessons[lesson_id]['project_id']

            # Create a new workspace
            response = SECOApi.create_workspace(
                project_id,
                workspace_token_required=True,
                # Uncomment if you want to change inactivity timeout
                # inactivity_timeout=20,
                # Uncomment if you want to allow to stopping a workspace instead of removing it after user inactivity
                # retention_time_stopped=60*48, # 2 days
                # retention_time_total=60*24*7, # 7 days
                # Uncomment if you want to manually resume the workspace using the API when it is stopped
                # auto_resume=False,
            )
            app.logger.debug(f'POST /workspaces output: {response}')

            # Prepare data to return
            workspace = {
                'id': response['workspace']['id'],
                'workspace_token': response['workspace']['workspace_token'],
            }

            # Assign the workspace ID to the user
            lesson_workspaces[user_id] = response['workspace']['id']
        except SECOApi.APIError as e:
            app.logger.debug(e)
            return jsonify({'error': "couldn't create a workspace"}), 422

    # If we don't have the workspace data it means that the frontend must make request again
    if not workspace:
        return jsonify({'error': "couldn't get the workspace"}), 422

    return jsonify({
        'error': None,
        'workspace': workspace,
    })


def is_logged_in() -> bool:
    return True


def get_user_id() -> int:
    return 1
