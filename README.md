Browtop: Real-Time Server Monitoring Application
Our Project Description
Browtop is an intuitive server monitoring tool designed to offer real-time insights into system performance metrics. It provides a seamless web-based interface that empowers users to track critical system statistics like CPU usage, memory consumption, active processes, and more. With its responsive design and secure communication, Browtop is ideal for administrators who need a comprehensive yet straightforward solution for monitoring their server environments.
________________________________________
Design Choices
Backend
•	Language & Framework: Python, chosen for its simplicity and rich ecosystem, paired with aiohttp for robust asynchronous WebSocket handling.
•	Libraries:
o	psutil: Selected for its efficient system and process management capabilities.
o	aiohttp: Enables real-time WebSocket communication, ensuring low-latency updates.
•	Authentication: Implemented a lightweight username/password system for simplicity. While the password is hardcoded for this project, secure methods (e.g., environment variables) are recommended for production environments.
•	Containerization: The entire application is Dockerized, ensuring portability and ease of deployment across diverse platforms.
Frontend
•	HTML & CSS: Built with a mobile-first approach to ensure accessibility and responsiveness on various devices.
•	JavaScript:
o	Manages WebSocket connections for efficient data exchange.
o	Dynamically updates UI components in real-time based on server responses.
o	Periodically refreshes system metrics to maintain accurate and up-to-date information.
________________________________________
Getting Started
Prerequisites
•	Docker
•	Docker Compose
•	Modern web browser



Setup Instructions


1.	Clone the Repository:
git clone https://github.com/furkanakbag/BrowTop.git
cd Browtop 

2.	Build and Start the Docker Container:
docker compose up --build -d --remove-orphans
3.	Access the Application:
o	Open your browser and navigate to :
https://cs395.org/1022/monitor
4.	Login Credentials:
o	Username: Any valid string
o	Password: 123
________________________________________
Features
User Authentication
•	Implements a simple login system to restrict access, ensuring that only authorized users can view system statistics.
•	Provides feedback on authentication success or failure to enhance the user experience.
Detailed System Insights
•	CPU Metrics: Monitors and displays real-time CPU usage as a percentage, giving an instant view of system load.
•	Memory Overview: Breaks down memory usage into used and total, displayed as percentages and absolute values.
•	Disk Health: Offers disk usage statistics, including space utilized and remaining capacity, critical for storage management.
•	Load Average: Reports system load over 1, 5, and 15-minute intervals, helping assess overall performance trends.
Advanced Process Management
•	Top Processes: Automatically highlights the top 10 resource-consuming processes based on CPU usage, ensuring visibility of high-demand applications.
•	Process Summary: Categorizes running processes into states such as running, sleeping, stopped, or zombie, providing a holistic view of process health.
Comprehensive Logging
•	System Logs: Displays the last 50 lines of the system log, offering valuable insights into system events and potential issues.
•	User Tracking: Lists currently logged-in users and recent login history, aiding in user activity monitoring and auditing.
Secure Real-Time Communication
•	Encryption: Uses TLS encryption for secure WebSocket communication, safeguarding data exchange between the server and client.
•	Efficient Updates: Maintains a low-latency connection to ensure real-time updates of system metrics and user activity.
Responsive and User-Friendly Interface
•	Designed with a focus on clarity and usability, making it easy for administrators to access vital data quickly.
•	Mobile-responsive design ensures compatibility with various devices, allowing monitoring on the go.
________________________________________
Security Note
Important: For this project, the password is stored in plaintext in the code for simplicity. ________________________________________
License
Our project is licensed under the MIT License. See the LICENSE file for details.
________________________________________

Contributors
•	Ömer Furkan Akbağ (furkanakbag)
•	Arda Küçük (ardakucuk0)
________________________________________



GitHub Repository
Github Repo Link : https://github.com/furkanakbag/BrowTop.git
•	Reviewer 1: furkanakbag
•	Reviewer 2: ardakucuk0


