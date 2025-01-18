# GitHub Repository Fetcher

This program fetches repositories from GitHub based on a search query and sends the repository information to a Microsoft Teams channel using an adaptive card.

## Configuration

### .env File

Create a `.env` file in the root directory of the project and add the following line:

```
GITHUB_TOKEN=YOUR_TOKEN
```

Replace `YOUR_TOKEN` with your actual GitHub personal access token.

### Generating a GitHub Token

1. Go to [GitHub Settings](https://github.com/settings/tokens).
2. Click on **Generate new token**.
3. Select the scopes you need. For this program, you will need at least the `repo` scope.
4. Click **Generate token**.
5. Copy the generated token and add it to your `.env` file as shown above.

**Note:** Ensure you generate a classic token and add SSO Authorization as a second step for enterprise organizations.

## Running the Program

1. Install the required Python packages:
    ```
    pip install -r requirements.txt
    ```

2. Run the script:
    ```
    python get-hub-repositories.py
    ```

The script will fetch repositories based on the search query and send the information to the specified Microsoft Teams channel.
