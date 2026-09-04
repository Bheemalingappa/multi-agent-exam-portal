import unittest
from app.schemas.events import RealtimeEventSchema

class TestRealtimeEventsSchema(unittest.TestCase):

    def test_realtime_event_schema_instantiation(self):
        evt = RealtimeEventSchema(
            event_type="EVALUATION_STAGE_CHANGED",
            attempt_id="att_123",
            submission_id="sub_456",
            progress=55,
            payload={"stage": "ANOMALY_ANALYSIS"}
        )
        self.assertEqual(evt.event_type, "EVALUATION_STAGE_CHANGED")
        self.assertEqual(evt.progress, 55)
        self.assertIsNotNone(evt.event_id)
        self.assertIsNotNone(evt.timestamp)

if __name__ == "__main__":
    unittest.main()
