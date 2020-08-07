"""
integration tests for mac_service
"""

import plistlib

import salt.utils.files
from tests.support.case import ModuleCase
from tests.support.helpers import (
    destructiveTest,
    runs_on,
    skip_if_binaries_missing,
    skip_if_not_root,
    slowTest,
)


@skip_if_not_root
@runs_on(kernel="Darwin")
@skip_if_binaries_missing("launchctl", "plutil")
class MacServiceModuleTest(ModuleCase):
    """
    Validate the mac_service module
    """

    SERVICE_NAME = "com.salt.integration.test"
    SERVICE_PATH = "/Library/LaunchDaemons/com.salt.integration.test.plist"

    def setUp(self):
        """
        setup our test launch service.
        """
        service_data = {
            "KeepAlive": True,
            "Label": self.SERVICE_NAME,
            "ProgramArguments": ["/bin/sleep", "1000"],
            "RunAtLoad": True,
        }
        with salt.utils.files.fopen(self.SERVICE_PATH, "rb") as fp:
            plistlib.dump(service_data, fp)
        self.run_function("service.enable", [self.SERVICE_NAME])
        self.run_function("service.start", [self.SERVICE_NAME])

    def tearDown(self):
        """
        stop and remove our test service.
        """
        self.run_function("service.stop", [self.SERVICE_NAME])
        salt.utils.files.safe_rm(self.SERVICE_PATH)

    @slowTest
    def test_show(self):
        """
        Test service.show
        """
        # Existing Service
        service_info = self.run_function("service.show", [self.SERVICE_NAME])
        self.assertIsInstance(service_info, dict)
        self.assertEqual(service_info["plist"]["Label"], self.SERVICE_NAME)

        # Missing Service
        self.assertIn(
            "Service not found", self.run_function("service.show", ["spongebob"])
        )

    @slowTest
    def test_launchctl(self):
        """
        Test service.launchctl
        """
        # Expected Functionality
        self.assertTrue(
            self.run_function("service.launchctl", ["error", "bootstrap", 64])
        )
        self.assertEqual(
            self.run_function(
                "service.launchctl", ["error", "bootstrap", 64], return_stdout=True
            ),
            "64: unknown error code",
        )

        # Raise an error
        self.assertIn(
            "Failed to error service",
            self.run_function("service.launchctl", ["error", "bootstrap"]),
        )

    @slowTest
    def test_list(self):
        """
        Test service.list
        """
        # Expected Functionality
        self.assertIn("PID", self.run_function("service.list"))
        self.assertIn("{", self.run_function("service.list", [self.SERVICE_NAME]))

        # Service not found
        self.assertIn(
            "Service not found", self.run_function("service.list", ["spongebob"])
        )

    @destructiveTest
    @slowTest
    def test_enable(self):
        """
        Test service.enable
        """
        self.assertTrue(self.run_function("service.enable", [self.SERVICE_NAME]))

        self.assertIn(
            "Service not found", self.run_function("service.enable", ["spongebob"])
        )

    @destructiveTest
    @slowTest
    def test_disable(self):
        """
        Test service.disable
        """
        self.assertTrue(self.run_function("service.disable", [self.SERVICE_NAME]))

        self.assertIn(
            "Service not found", self.run_function("service.disable", ["spongebob"])
        )

    @destructiveTest
    @slowTest
    def test_start(self):
        """
        Test service.start
        Test service.stop
        Test service.status
        """
        self.assertTrue(self.run_function("service.start", [self.SERVICE_NAME]))

        self.assertIn(
            "Service not found", self.run_function("service.start", ["spongebob"])
        )

    @destructiveTest
    @slowTest
    def test_stop(self):
        """
        Test service.stop
        """
        self.assertTrue(self.run_function("service.stop", [self.SERVICE_NAME]))

        self.assertIn(
            "Service not found", self.run_function("service.stop", ["spongebob"])
        )

    @destructiveTest
    @slowTest
    def test_status(self):
        """
        Test service.status
        """
        # A running service
        self.assertTrue(self.run_function("service.start", [self.SERVICE_NAME]))
        self.assertTrue(self.run_function("service.status", [self.SERVICE_NAME]))

        # A stopped service
        self.assertTrue(self.run_function("service.stop", [self.SERVICE_NAME]))
        self.assertFalse(self.run_function("service.status", [self.SERVICE_NAME]))

        # Service not found
        self.assertFalse(self.run_function("service.status", ["spongebob"]))

    @slowTest
    def test_available(self):
        """
        Test service.available
        """
        self.assertTrue(self.run_function("service.available", [self.SERVICE_NAME]))
        self.assertFalse(self.run_function("service.available", ["spongebob"]))

    @slowTest
    def test_missing(self):
        """
        Test service.missing
        """
        self.assertFalse(self.run_function("service.missing", [self.SERVICE_NAME]))
        self.assertTrue(self.run_function("service.missing", ["spongebob"]))

    @destructiveTest
    @slowTest
    def test_enabled(self):
        """
        Test service.enabled
        """
        self.assertTrue(self.run_function("service.enabled", [self.SERVICE_NAME]))
        self.assertTrue(self.run_function("service.start", [self.SERVICE_NAME]))

        self.assertTrue(self.run_function("service.enabled", [self.SERVICE_NAME]))
        self.assertTrue(self.run_function("service.stop", [self.SERVICE_NAME]))

        self.assertTrue(self.run_function("service.enabled", ["spongebob"]))

    @destructiveTest
    @slowTest
    def test_disabled(self):
        """
        Test service.disabled
        """
        SERVICE_NAME = "com.apple.nfsd"
        self.assertTrue(self.run_function("service.start", [SERVICE_NAME]))
        self.assertFalse(self.run_function("service.disabled", [SERVICE_NAME]))

        self.assertTrue(self.run_function("service.disable", [SERVICE_NAME]))
        self.assertTrue(self.run_function("service.disabled", [SERVICE_NAME]))
        self.assertTrue(self.run_function("service.enable", [SERVICE_NAME]))
        self.assertIn(
            "Service not found", self.run_function("service.stop", ["spongebob"])
        )

    @slowTest
    def test_get_all(self):
        """
        Test service.get_all
        """
        services = self.run_function("service.get_all")
        self.assertIsInstance(services, list)
        self.assertIn(self.SERVICE_NAME, services)

    @slowTest
    def test_get_enabled(self):
        """
        Test service.get_enabled
        """
        services = self.run_function("service.get_enabled")
        self.assertIsInstance(services, list)
        self.assertIn("com.apple.coreservicesd", services)
