from locust import FastHttpUser, between, task


class PsychologyLoad(FastHttpUser):
    wait_time = between(0, 0)

    @task
    def chat(self):
        self.client.post(
            "/v1/psychology/chat",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )


def test_load(monkeypatch):
    import gevent
    from locust.env import Environment

    env = Environment(user_classes=[PsychologyLoad])
    env.create_local_runner()
    env.runner.start(user_count=1, spawn_rate=10)
    gevent.sleep(30)
    env.runner.quit()
    assert env.stats.total.fail_ratio < 0.01
