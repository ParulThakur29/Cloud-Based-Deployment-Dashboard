import docker

client = docker.from_env()

def deploy_app(image_name):
    container = client.containers.run(image_name, detach=True)
    return container.id

def stop_app(container_id):
    container = client.containers.get(container_id)
    container.stop()