# ChatViz
### Team: Kunal Mundada | Ty Feng

## Dev Setup

1. Clone this repository.

3. Navigate into the project directory

4. Create a new virtual environment and activate it:

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

7. Add your [HuggingFace Hub Access key](https://beta.openai.com/account/api-keys) to the newly created `.env` file.

8. Make sure you either have the original dataset in the `data/orig` folder or you generate them in the next step.

8. Run the app from outside the directory:

   ```bash
   $ python -m ChatViz
   ```