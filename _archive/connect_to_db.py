import os
import yaml
from pymongo import MongoClient, errors

# Get the path of the current script
scriptPath = os.path.dirname(os.path.abspath(__file__))

class MongoDB:
    def __init__(self, config_file="config.yml"):
        """
        Initializes MongoDB connection using a YAML configuration file.
        
        :param config_file: Path to the YAML config file (default: config.yml)
        """
        self.config_file = config_file
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.auth_db = None
        self.db_name = None
        self.client = None

        self.load_config()
        self.connect()

    def load_config(self):
        """Loads MongoDB credentials from the YAML file."""
        try:
            config_path = os.path.join(scriptPath, self.config_file)
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
                self.host = config["mongodb"]["host"]
                self.port = config["mongodb"]["port"]
                self.username = config["mongodb"].get("username", None)
                self.password = config["mongodb"].get("password", None)
                self.auth_db = config["mongodb"]["auth_db"]
                self.db_name = config["mongodb"]["db_name"]
                print("✅ Configuration loaded successfully!")

        except Exception as e:
            raise RuntimeError(f"❌ Error loading YAML configuration: {e}")

    def connect(self):
        """Connects to MongoDB using the loaded configuration."""
        try:
            if self.username and self.password:
                uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.auth_db}"
            else:
                uri = f"mongodb://{self.host}:{self.port}/{self.auth_db}"

            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")  # Test connection
            print("✅ Connected to MongoDB successfully!")

        except errors.ServerSelectionTimeoutError:
            raise RuntimeError("❌ MongoDB connection timeout! Please check your connection.")
        except Exception as e:
            raise RuntimeError(f"❌ Error connecting to MongoDB: {e}")

    def database_exists(self):
        """Checks if the database exists in MongoDB."""
        if self.client:
            try:
                return self.db_name in self.client.list_database_names()
            except Exception as e:
                print(f"❌ Error checking database existence: {e}")
                return False
        return False

    def get_database(self):
        """Returns the MongoDB database instance if it exists."""
        if not self.client:
            print("⚠️ No MongoDB client connection available.")
            return None

        if self.database_exists():
            print(f"✅ Database '{self.db_name}' found!")
            return self.client[self.db_name]
        else:
            print(f"❌ Database '{self.db_name}' does not exist!")
            return None

    def close(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed successfully!")

# Example Usage
if __name__ == "__main__":
    try:
        mongo   = MongoDB("config.yml")
        db      = mongo.get_database()
        mongo.close()
    except Exception as e:
        print(e)
