from main import MasterAgent, WorkerAgent

# Function to load transcript from a text file
def load_transcript(file_path):
    with open(file_path, 'r') as file:
        transcript = file.read()
    return transcript

# Path to the transcript file
transcript_file = 'transcript.txt'

# Load the transcript
transcript_text = load_transcript(transcript_file)

# Initialize MasterAgent and pass the transcript text to run()
master_agent = MasterAgent()
master_agent.run(transcript_text)
