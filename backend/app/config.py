import os


def _load_yaml_env(yaml_path: str) -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    if not os.path.isfile(yaml_path):
        return {}
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    return {item["name"]: str(item["value"]) for item in data.get("env", [])}


_DEPLOY_MODE = os.environ.get("AUTH_MODE")

if _DEPLOY_MODE is None:
    # Running locally — read env vars from app.yaml
    _cfg = _load_yaml_env(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app.yaml")
    )
    def _env(key: str, default: str = "") -> str:
        return _cfg.get(key, default)
else:
    # Running on Databricks Apps — env vars already injected by platform
    def _env(key: str, default: str = "") -> str:
        return os.environ.get(key, default)


AUTH_MODE: str = _env("AUTH_MODE", "LOCAL")
DATABASE_URL: str = _env("DATABASE_URL")
