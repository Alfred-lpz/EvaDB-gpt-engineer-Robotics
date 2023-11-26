import openai
import json
from evadb import EvaDB

class AI:
    def __init__(self, evadb_config, **kwargs):
        self.kwargs = kwargs
        self.evadb = EvaDB(evadb_config)

        try:
            openai.Model.retrieve("gpt-4")
        except openai.error.InvalidRequestError:
            print(
                "Model gpt-4 not available for provided api key reverting "
                "to gpt-3.5.turbo. Sign up for the gpt-4 wait list here: "
                "https://openai.com/waitlist/gpt-4-api"
            )
            self.kwargs["model"] = "gpt-3.5-turbo"

    def start(self, system, user):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        return self.next(messages)

    def fsystem(self, msg):
        return {"role": "system", "content": msg}

    def fuser(self, msg):
        return {"role": "user", "content": msg}

    def fassistant(self, msg):
        return {"role": "assistant", "content": msg}

    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages = messages + [{"role": "user", "content": prompt}]

        response = openai.ChatCompletion.create(
            messages=messages, stream=True, **self.kwargs
        )

        chat = []
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            msg = delta.get("content", "")
            print(msg, end="")
            chat.append(msg)

        # Store the conversation in EvaDB
        self.store_conversation(messages + [{"role": "assistant", "content": "".join(chat)}])

        return messages + [{"role": "assistant", "content": "".join(chat)}]

    def store_conversation(self, conversation):
        # Convert conversation to a format suitable for storage
        conversation_data = json.dumps(conversation)

        # Using a parameterized query for security
        query = "INSERT INTO conversations (data) VALUES (%s)"
        self.evadb.cursor.execute(query, (conversation_data,))
        self.evadb.connection.commit()

    def query_robotics_data(self, query_parameters):
        # Constructing a safe query based on parameters
        query = "SELECT * FROM robotics_data WHERE "
        query_conditions = ["%s = %s" % (key, '%s') for key in query_parameters]
        query += " AND ".join(query_conditions)

        # Executing the query using parameterized approach
        self.evadb.cursor.execute(query, list(query_parameters.values()))
        results = self.evadb.cursor.fetchall()

        # Convert the results to a suitable format
        data = [dict(row) for row in results]
        return data
