# PITA

PITA is software that converts vendor invoice PDFs into machine-readable EDI files.

## Getting Started
The instructions below will help you set up a local development and testing environment.  
PITA is flexible and can be used in a variety of contexts—including GitHub Codespaces, a Python virtual environment, Docker, or directly in VS Code.  
This guide focuses on setup and usage within VS Code.

### Prerequisites

- **Docker Desktop**: Make sure Docker Desktop is installed and running on your system.  
- **VS Code Extension**: Install the *Dev Containers* extension in VS Code.  



### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Open in a Dev Container**  
   - In VS Code, open the cloned folder.  
   - Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and choose **Dev Containers: Open Folder in Container...**  
   - Choose your folder and the From Dockerfile option.
   - VS Code will build the container (if needed) and attach your workspace to it.  

### Using PITA

Once the container is running, you can interact with the project files directly.  
To process vendor invoice PDFs:

1. Upload one or more PDF files into the project directory.  
2. Run the program:  
   ```bash
   python main.py
   ```

The program will report each PDF processed, each EDI file created, and display the total number of invoices at the end.

The next step is importing all the *.edi files into your Library Services Platform with your favourite method.

## Running Tests

To run the test suite inside the container, open a terminal and run:

```bash
pytest
```

## License

This project is licensed under the New BSD License.  
See the [LICENSE.txt](LICENSE.txt) file for details.
