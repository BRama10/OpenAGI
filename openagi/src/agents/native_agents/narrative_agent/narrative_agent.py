
from ...base import BaseAgent

import time

from ...agent_process import (
    AgentProcess
)

import numpy as np

import argparse

from concurrent.futures import as_completed

class NarrativeAgent(BaseAgent):
    def __init__(self,
                 agent_name,
                 task_input,
                 llm,
                 agent_process_queue,
                 agent_process_factory,
                 log_mode: str
        ):
        BaseAgent.__init__(self, agent_name, task_input, llm, agent_process_queue, agent_process_factory, log_mode)
        # print(self.log_mode)

    def run(self):
        request_waiting_times = []
        request_turnaround_times = []
        prompt = ""
        prefix = self.prefix
        prompt += prefix
        task_input = self.task_input
        task_input = "The task you need to solve is: " + task_input
        self.logger.log(f"{task_input}\n", level="info")
        # print(f"[{self.agent_name}] {task_input}\n")

        prompt += task_input

        steps = [
            "develop the story's setting and characters, establish a background and introduce the main characters.",
            "given the background and characters, create situations that lead to the rising action, develop the climax with a significant turning point, and then move towards the resolution.",
            "conclude the story and reflect on the narrative. This could involve tying up loose ends, resolving any conflicts, and providing a satisfactory conclusion for the characters."
        ]

        rounds = 0

        for i, step in enumerate(steps):
            prompt += f"\nIn step {i+1}, you need to {step}. Output should focus on current step and don't be verbose!"

            self.logger.log(f"Step {i+1}: {step}\n", level="info")

            response, start_times, end_times, waiting_times, turnaround_times = self.get_response(prompt)

            if rounds == 0:
                self.set_start_time(start_times[0])

            rounds += 1

            request_waiting_times.extend(waiting_times)
            request_turnaround_times.extend(turnaround_times)

            prompt += f"The solution to step {i+1} is: {response}\n"

            self.logger.log(f"The solution to step {i+1}: {response}\n", level="info")

            prompt += response

        prompt += f"Given the interaction history: '{prompt}', integrate content in each step to give a full story, don't be verbose!"

        final_result, start_times, end_times, waiting_times, turnaround_times = self.get_response(prompt)
        request_waiting_times.extend(waiting_times)
        request_turnaround_times.extend(turnaround_times)

        self.set_status("done")
        self.set_end_time(time=time.time())

        self.logger.log(f"{task_input} Final result is: {final_result}\n", level="info")

        return {
            "agent_name": self.agent_name,
            "result": final_result,
            "rounds": rounds,
            "agent_waiting_time": self.start_time - self.created_time,
            "agent_turnaround_time": self.end_time - self.created_time,
            "request_waiting_times": request_waiting_times,
            "request_turnaround_times": request_turnaround_times,
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run NarrativeAgent')
    parser.add_argument("--agent_name")
    parser.add_argument("--task_input")

    args = parser.parse_args()
    agent = NarrativeAgent(args.agent_name, args.task_input)

    agent.run()