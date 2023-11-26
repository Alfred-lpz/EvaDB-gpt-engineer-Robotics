import re
import json
import evadb

def parse_chat(chat):
    # Define robotics-related keywords
    robotics_keywords = ["robot", "sensor", "actuator", "control algorithm", "kinematics", "dynamics"]

    # Logic to parse chat for robotics-related content
    robotics_related_content = []
    for line in chat.split('\n'):
        if any(keyword in line.lower() for keyword in robotics_keywords):
            robotics_related_content.append(line)

    # Existing logic to split chat and extract code blocks
    split_chat = chat.split("*CODEBLOCKSBELOW*")
    is_token_found = len(split_chat) > 1
    readme = split_chat[0].strip() if is_token_found else "No readme"
    code_blocks = split_chat[1] if is_token_found else chat

    regex = r"(\S+?)\n```\S+\n(.+?)```"
    matches = re.finditer(regex, code_blocks, re.DOTALL)
    files = []
    for match in matches:
        path = re.sub(r'[<>\"|?*]', "", match.group(1))
        code = match.group(2)
        files.append((path, code))

    files.append(("README.txt", readme))
    return files, '\n'.join(robotics_related_content)

def to_files(chat, workspace):
    # Initialize EvaDB connection
    db = evadb.connect()
    cursor = db.cursor()

    # Store the entire chat in EvaDB
    query = "INSERT INTO chat_logs (chat_content) VALUES (%s)"
    cursor.execute(query, (json.dumps(chat),))
    db.commit()

    # Parse the chat and extract robotics-related content
    files, robotics_content = parse_chat(chat)

    # Store the parsed files and robotics content
    workspace["all_output.txt"] = chat
    workspace["robotics_content.txt"] = robotics_content
    for file_name, file_content in files:
        workspace[file_name] = file_content

    # Additional logic for robotics-specific outputs
    if robotics_content:
        # Generate a configuration file for motion path planning
        config_file_content = generate_robot_config(robotics_content)
        workspace["robot_config.txt"] = config_file_content

        # Analyze the robotics content for motion path planning
        analysis_report = analyze_robotics_data(robotics_content)
        workspace["robotics_analysis_report.txt"] = analysis_report

    # Close the database connection
    db.close()

def generate_robot_config(content):
    # Extract parameters for motion path planning
    speed = "default_speed: 1.0 m/s"  # Default speed
    precision = "default_precision: 0.01 m"  # Default precision
    waypoints = "waypoints: [0,0,0], [1,1,1], [2,2,2]"  # Example waypoints

    config = f"Motion Path Planning Configuration\n{speed}\n{precision}\n{waypoints}"
    return config

def analyze_robotics_data(content):
    # Keywords related to motion path planning
    keywords = ["path", "trajectory", "obstacle", "navigation", "waypoint"]

    # Analyze content for mentions of these keywords
    analysis_results = []
    for line in content.split('\n'):
        if any(keyword in line.lower() for keyword in keywords):
            analysis_results.append(line)

    summary = "Motion Path Planning Analysis Report\n"
    summary += "\n".join(analysis_results) if analysis_results else "No relevant motion path planning content found."

    return summary
