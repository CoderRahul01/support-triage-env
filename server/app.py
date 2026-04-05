"""FastAPI application for the Support Triage Environment."""
import os

try:
    from openenv.core.env_server.http_server import create_app
    from ..models import SupportAction, SupportObservation
    from ..environment import SupportTriageEnvironment
except ImportError:
    from openenv.core.env_server.http_server import create_app
    from models import SupportAction, SupportObservation
    from environment import SupportTriageEnvironment


def create_support_triage_environment() -> SupportTriageEnvironment:
    """Factory: creates one SupportTriageEnvironment per session."""
    return SupportTriageEnvironment()


app = create_app(
    create_support_triage_environment,
    SupportAction,
    SupportObservation,
    env_name="support_triage_env",
    max_concurrent_envs=16,
)


def main() -> None:
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
