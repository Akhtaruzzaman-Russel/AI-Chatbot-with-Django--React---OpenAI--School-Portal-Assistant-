from importlib import reload
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

import uniapp.views as views


class ChatViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_chat_view_returns_mock_reply_when_openai_key_is_missing(self):
        with patch.object(settings, "OPENAI_API_KEY", None), patch("uniapp.views.os.getenv", return_value=None):
            reload(views)
            response = self.client.post(
                reverse("chat_with_unihelp"),
                {"message": "Hello"},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("mock reply", response.json()["response"].lower())
