# PDFA_Applied_Databases_Project
ATU-PDFA Applied Databases Project


## Instruction

1. Clone the repository to your local machine using the following command:
   ```
   git clone https://github.com/clydewatts1/PDFA_Applied_Databases_Project
    ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```



### WSL Setup

sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 -m venv venv_wsl
source venv_wsl/bin/activate

Fix localhost issue
ip route show default | awk '{print $3}'
172.28.0.1


-- 1. Create a network-accessible root user (replace with your actual password)
CREATE USER 'root'@'%' IDENTIFIED BY 'root';

-- 2. Give this user full access to everything
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';

-- 3. Apply the changes immediately
FLUSH PRIVILEGES;

pip install pexpect pytest