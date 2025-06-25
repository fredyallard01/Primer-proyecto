from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def blog_home(self):
        self.client.get("/")

    @task
    def view_post(self):
        self.client.get("/blog/4/")
    @task
    def view_post(self):
        self.client.get("/blog/5/")
    @task
    def view_post(self):
        self.client.get("/blog/6/")
    @task
    def view_post(self):
        self.client.get("/blog/7/")