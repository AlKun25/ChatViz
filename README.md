# ChatViz
### Team: Kunal Mundada | Ty Feng

## Dev Setup

1. Clone this repository.

2. Navigate into the project directory

3. Create a new virtual environment and activate it:

   ```bash
   $ python -m venv venv
   $ source ./venv/bin/activate
   ```

4. Install the Python package requirements:

   ```bash
   $ cd backend
   $ pip install -r requirements.txt
   
   ```
5. Install the Node modules requirements:
   ```bash
   $ cd frontend
   $ npm install .
   ```

6. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

7. Add your [HuggingFace Hub Access key](https://beta.openai.com/account/api-keys) to the newly created `.env` file.


8. Run the server from within project folder:

   ```bash
   $ python backend/server.py
   ```
   You will see the Flask server running at port 8000. 


9. Run the application:
   ```bash
   $ cd frontend
   $ npm run dev

   ```
   You will see your application running at port 3000.




