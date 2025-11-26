"""Secure credential storage using libsecret (GNOME Keyring)."""

import gi

gi.require_version("Secret", "1")
from gi.repository import Secret

# Define schema for our credentials
SCHEMA = Secret.Schema.new(
    "org.andypiper.SimpleAnalyticsViewer",
    Secret.SchemaFlags.NONE,
    {
        "credential-type": Secret.SchemaAttributeType.STRING,
    },
)


class CredentialManager:
    """Manages secure storage of API credentials in the system keyring."""

    @staticmethod
    def store_api_key(api_key: str) -> bool:
        """
        Store API key securely in system keyring.

        Args:
            api_key: The Simple Analytics API key to store

        Returns:
            True if stored successfully
        """
        return Secret.password_store_sync(
            SCHEMA,
            {"credential-type": "api-key"},
            Secret.COLLECTION_DEFAULT,
            "Simple Analytics API Key",
            api_key,
            None,
        )

    @staticmethod
    def retrieve_api_key() -> str | None:
        """
        Retrieve API key from secure storage.

        Returns:
            The API key if found, None otherwise
        """
        return Secret.password_lookup_sync(
            SCHEMA, {"credential-type": "api-key"}, None
        )

    @staticmethod
    def clear_api_key() -> bool:
        """
        Remove API key from secure storage.

        Returns:
            True if removed successfully
        """
        return Secret.password_clear_sync(
            SCHEMA, {"credential-type": "api-key"}, None
        )

    @staticmethod
    def store_user_id(user_id: str) -> bool:
        """
        Store user ID securely in system keyring.

        Args:
            user_id: The Simple Analytics user ID to store

        Returns:
            True if stored successfully
        """
        return Secret.password_store_sync(
            SCHEMA,
            {"credential-type": "user-id"},
            Secret.COLLECTION_DEFAULT,
            "Simple Analytics User ID",
            user_id,
            None,
        )

    @staticmethod
    def retrieve_user_id() -> str | None:
        """
        Retrieve user ID from secure storage.

        Returns:
            The user ID if found, None otherwise
        """
        return Secret.password_lookup_sync(
            SCHEMA, {"credential-type": "user-id"}, None
        )

    @staticmethod
    def clear_user_id() -> bool:
        """
        Remove user ID from secure storage.

        Returns:
            True if removed successfully
        """
        return Secret.password_clear_sync(
            SCHEMA, {"credential-type": "user-id"}, None
        )

    @staticmethod
    def clear_all() -> None:
        """Clear all stored credentials."""
        CredentialManager.clear_api_key()
        CredentialManager.clear_user_id()
