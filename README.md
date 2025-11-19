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
   $ pip install -r requirements.txt
   
   ```
5. Install the Node modules requirements:
   ```bash
   $ cd frontend
   $ npm install 
   ```

6. (Optional) Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

7. (Optional, only required if you're downloading the dataset from HuggingFace or need to process the dataset) Add your [HuggingFace Hub Access key](https://huggingface.co/docs/hub/security-tokens) to the newly created `.env` file. Also add your OpenAI API key to the `.env` file for GPT-4 cluster summary generation.

Instead of processing the data yourself, you can use our already processed data in the `frontend/data/proc` folder.


8. Run the server from within project folder:

   ```bash
   $ cd backend
   $ python backend/server.py
   ```
   You will see the Flask server running at port 8000. This is used for real-time sentiment analysis, because the csv files are already too big to add a new field.


9. Run the application:
   ```bash
   $ cd frontend
   $ npm run dev

   ```
   You will see your application running at port 3000.




