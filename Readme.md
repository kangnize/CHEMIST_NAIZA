# Dependencies

## SETUP
1. Clone the package
   ```sh
   git clone https://github.com/kangnize/CHEMIST_NAIZA.git
   ```
2. Create a virtual environment
   ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install all the required dependencies in the create venv
   ```sh
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root folder with the structure of `.env.example`
5. How to run the app
   - TODO: Add steps

## GITIGNORE
Ignore files that are not required e.g. secret files, dependencies' libraries


## Virtual Environment
### Create a virtual environment
```sh
# Create new virtual environment
python3 -m venv venv
source venv/bin/activate
python3 -m pip install xyz

# Activate an existing virtual environment
source venv/bin/activate
```
### Shows packages in venv
`pip list`

### Install all dependencies
`pip install -r requirements.txt`