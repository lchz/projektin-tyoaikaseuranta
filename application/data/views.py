from application import app, db, login_required
from flask import render_template, request, redirect, url_for
from flask_login import current_user

from application.projects.models import Project
from application.auth.models import User
from application.tasks.models import Task
from application.data.forms import DataForm

from datetime import timedelta


@app.route('/projects/<project_id>/data', methods=['GET', 'POST'])
@login_required(role='MASTER')
def project_data(project_id):

    project = Project.query.get(project_id)
    participants = Task.find_project_participants(project_id)
    timeData = Task.time_of_project(project_id)

    for p in participants:
        taskData = Task.find_tasks_of_participant(project.id, p.get('accountId'))

        uncom = taskData[0].get('uncom')
        com = taskData[1].get('com')
        total = taskData[2].get('total')

        p['total'] = total
        p['uncom'] = uncom
        p['com'] = com

    timeWeek = None
    fromDate = None
    toDate = None

    if request.method == 'POST':
        form = DataForm(request.form)

        if not form.validate():
            return render_template('/data/dataProject.html',
                        form=DataForm(),
                        project=project,
                        data=participants,
                        timeData=timeData)

        fromDate = form.fromDate.data
        toDate = fromDate + timedelta(days=7)

        searchFrom = fromDate - timedelta(days=1)
        searchTo = toDate + timedelta(days=1)

        timeWeek = Task.time_of_one_week(project_id, searchFrom, searchTo, None)

    return render_template('/data/dataProject.html',
                            form=DataForm(),
                            project=project,
                            data=participants,
                            timeData=timeData,
                            timeWeek=timeWeek,
                            fromDate=fromDate,
                            toDate=toDate)


@app.route('/projects/<project_id>/data/tasks/<account_id>', methods=['GET'])
@login_required(role="ANY")
def tasks_data_of_participant(project_id, account_id):

    account = User.query.get(account_id)
    project = Project.query.get(project_id)
    tasks = Task.find_my_tasks(account_id, project_id)
    timeData = Task.time_of_person(project_id, account_id)

    return render_template('data/dataTasks.html', 
                            account=account,
                            project=project, 
                            tasks=tasks,
                            timeData=timeData)

@app.route('/projects/<project_id>/myData', methods=['GET', 'POST'])
@login_required(role="BASIC")
def my_project_data(project_id):

    project = Project.query.get(project_id)
    canSee = False

    for participant in project.participants:
        if participant.id == current_user.id:
            canSee = True
            break

    if not canSee:
        return render_template('projects/project.html', 
                                project=project,
                                creator=User.query.get(project.account_id),
                                canRegister=True,
                                notRegisteredError='Please register first.',
                                role='BASIC'
                              )
    
    myTimeData = Task.time_of_person(project_id, current_user.id)

    myTimeWeek = None
    fromDate = None
    toDate = None

    if request.method == 'POST':
        form = DataForm(request.form)

        if not form.validate():
            return render_template('/data/myData.html',
                        form=DataForm(),
                        project=project,
                        myTimeData=myTimeData)

        fromDate = form.fromDate.data
        toDate = fromDate + timedelta(days=7)

        searchFrom = fromDate - timedelta(days=1)
        searchTo = toDate + timedelta(days=1)

        myTimeWeek = Task.time_of_one_week(project_id, searchFrom, searchTo, current_user.id)

    return render_template('data/myData.html',
                            project=project,
                            account=current_user,
                            form=DataForm(),
                            myTimeData=myTimeData,
                            fromDate=fromDate,
                            toDate=toDate,
                            myTimeWeek=myTimeWeek)


@app.route('/projects/<project_id>/data/remove/<account_id>', methods=['POST'])
@login_required(role="MASTER")
def remove_participant_from_project(project_id, account_id):

    Task.remove_person_from_project(project_id, account_id)

    return redirect(url_for('project_data', project_id=project_id))
