# Project Features

- Customize server name
- Create new Deployment
- Update Deployed Project
- Delete Deployed Project
- Monitoring Deployed Project
- Load balancing

## Customize server name
Allow User to manage DNS records for their domains.
**Feature**
- customize server name
- manage DNS records

## Create new Deployment
User can create a new deployment by specifying the project details, environment, and configuration settings.

**Feature**
- choosing project types: nextjs, nuxtjs, nodejs,...
- auto recommend for project service (supervisorctl, systemd, pm2, docker) (case system has existing docker)
- custom domain names (by default the domain `${project_name}.example.com`)
- environment settings
- configuration settings


## Update Deployed Project
User can update an existing deployment by modifying the project details, environment, and configuration settings.

**Feature**
- update project types
- update deployment service
- update domain names
- update environment settings
- update configuration settings

## Delete Deployed Project
User can delete an existing deployment by specifying the project details.

**Feature**
- delete project types
- delete deployment service
- delete domain names
- delete environment settings
- delete configuration settings

## Monitoring Deployed Project
User can monitor an existing deployment by viewing the project details, environment, and configuration settings.

**Feature**
- Monitor by Project
- Customize monitoring settings
- View monitoring metrics
- Set up alerts and notifications
- Generate monitoring reports

## Load balancing
User can configure load balancing for an existing deployment to distribute traffic across multiple instances.

**Feature**
- Configure load balancing settings
- Monitor load balancing performance
- Set up load balancing rules