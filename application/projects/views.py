from application import app, db, login_required
from flask import render_template, request, redirect, url_for
from flask_login import current_user
from application.projects.models import Project
from application.auth.models import User
from application.projects.forms import ProjectForm


@app.route('/projects', methods=['GET'])
def projects_index():
    return render_template('/projects/projectList.html', projects=Project.query.all())


@app.route('/projects/<project_id>', methods=['GET'])
@login_required(role="ANY")
def project_index(project_id):

    project = Project.query.get(project_id)
    role = current_user.roles[0].name
    creator = User.query.get(project.account_id)
    canRegister = True
    authorized = False

    if role == 'BASIC':
        for participant in project.participants:
            if participant.id == current_user.id:
                canRegister = False
                break

    elif role == 'MASTER':
        if creator.id == current_user.id:
            authorized = True
            
    return render_template('/projects/project.html', 
                            project=project, 
                            creator=creator,
                            canRegister=canRegister,
                            authorized=authorized,
                            role=role
                          )


@app.route('/projects/new')
@login_required(role="MASTER")
def projects_form():
    return render_template('projects/projectForm.html', form=ProjectForm())


@app.route('/projects', methods=['POST'])
@login_required(role="MASTER")
def projects_create():

    form = ProjectForm(request.form)

    if not form.validate():
        return render_template('projects/projectForm.html', form=form)

    project = Project(form.name.data, form.description.data)
    project.account_id = current_user.id

    db.session().add(project)
    db.session().commit()

    return redirect(url_for('projects_index'))


@app.route('/projects/<project_id>/register', methods=['POST'])
@login_required(role="BASIC")
def project_registration(project_id):

    try:
        project = Project.query.get(project_id)

        project.participants.append(current_user)

        db.session().commit()
        return redirect(url_for('projects_index'))
        
    except:
        return redirect(url_for('projects_index'))


@app.route('/projects/<project_id>/deletion', methods=['POST'])
@login_required(role="MASTER")
def project_deletion(project_id):

    try:
        project = Project.query.get(project_id)
        
        if project.account_id == current_user.id:
            Project.remove_project(project_id)

        return redirect(url_for('myPage'))

    except:
        return redirect(url_for('myPage'))


@app.route('/projects/<project_id>/modification/name', methods=['POST'])
@login_required(role="MASTER")
def project_modifiy_name(project_id):

    project = Project.query.get(project_id)
    name = request.form.get('set_project_name')

    if len(name) >= 5 and len(name) <= 144:
        project.name = name
        db.session().commit()

    return redirect(url_for('project_index', project_id=project.id))

@app.route('/projects/<project_id>/modification/description', methods=['POST'])
@login_required(role='MASTER')
def project_modifiy_description(project_id):

    project = Project.query.get(project_id)
    description = request.form.get('set_project_description')

    if len(description) >= 5 and len(description) <= 1000:
        project.description = description
        db.session().commit()

    return redirect(url_for('project_index', project_id=project.id))