import unittest

from requests import Response

from utils.chall_manager_error import build_cm_exception, build_error_payload


def _make_response(status_code: int, body: str, content_type: str = "application/json"):
    resp = Response()
    resp.status_code = status_code
    resp._content = body.encode("utf-8")
    resp.headers["Content-Type"] = content_type
    return resp


class TestErrorHandling(unittest.TestCase):
    def test_maps_grpc_code_to_http_status(self):
        resp = _make_response(
            500, '{"code":6,"message":"already exists","details":[]}'
        )
        exc = build_cm_exception(resp, "fallback")

        self.assertEqual(exc.code, 6)
        self.assertEqual(exc.http_status, 409)  # mapped from ALREADY_EXISTS
        self.assertEqual(exc.message, "already exists")

    def test_uses_body_when_not_json(self):
        resp = _make_response(502, "plain failure", content_type="text/plain")
        exc = build_cm_exception(resp, "fallback message")

        self.assertEqual(exc.message, "plain failure")
        self.assertEqual(exc.code, 502)
        self.assertEqual(exc.http_status, 502)

    def test_build_error_payload_adds_details(self):
        resp = _make_response(
            500,
            '{"code":14,"message":"service unavailable","details":["retry later"]}',
        )
        exc = build_cm_exception(resp, "fallback")
        payload, status = build_error_payload(exc)

        self.assertEqual(status, 503)  # grpc code 14 -> HTTP 503
        self.assertEqual(payload["message"], "service unavailable")
        self.assertEqual(payload["code"], 14)
        self.assertEqual(payload["details"], ["retry later"])


if __name__ == "__main__":
    unittest.main()
