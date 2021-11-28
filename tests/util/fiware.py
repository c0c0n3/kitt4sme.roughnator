import json
from typing import Optional
from uri import URI

from roughnator.util.ngsi.headers import FiwareContext
from roughnator.util.ngsi.orion import OrionClient


TENANT = 'csic'
ORION_EXTERNAL_BASE_URL = 'http://localhost:1026'
ROUGHNATOR_INTERNAL_BASE_URL = 'http://roughnator:8000'
QUANTUMLEAP_INTERNAL_BASE_URL = 'http://quantumleap:8668'
ROUGHNATOR_SUB = {
    "description": "Notify Roughnator of changes to any entity.",
    "subject": {
        "entities": [
            {
                "idPattern": ".*"
            }
        ]
    },
    "notification": {
        "http": {
            "url": f"{ROUGHNATOR_INTERNAL_BASE_URL}/updates"
        }
    }
}
QUANTUMLEAP_SUB = {
    "description": "Notify QuantumLeap of changes to any entity.",
    "subject": {
        "entities": [
            {
                "idPattern": ".*"
            }
        ]
    },
    "notification": {
        "http": {
            "url": f"{QUANTUMLEAP_INTERNAL_BASE_URL}/v2/notify"
        }
    }
}


def orion_client(service_path: Optional[str] = None,
                 correlator: Optional[str] = None) -> OrionClient:
    base_url = URI(ORION_EXTERNAL_BASE_URL)
    ctx = FiwareContext(service=TENANT, service_path=service_path,
                        correlator=correlator)
    return OrionClient(base_url, ctx)


class SubMan:

    def __init__(self):
        self._orion = orion_client()

    def create_roughnator_sub(self):
        self._orion.subscribe(ROUGHNATOR_SUB)

    def create_quantumleap_sub(self):
        self._orion.subscribe(QUANTUMLEAP_SUB)

    def create_subscriptions(self) -> [dict]:
        self.create_roughnator_sub()
        self.create_quantumleap_sub()
        return self._orion.list_subscriptions()

# NOTE. Subscriptions and FIWARE service path.
# The way it behaves for subscriptions is a bit counter intuitive.
# You'd expect that with a header of 'fiware-servicepath: /' Orion would
# notify you of changes to *any* entities in the tree, similar to queries.
# But in actual fact, to do that you'd have to omit the service path header,
# which is what we do here. Basically the way it works is that if you
# specify a service path, then Orion only considers entities right under
# the last node in the service path, but not any other entities that might
# sit further down below. E.g. if your service tree looks like (e stands
# for entity)
#
#                        /
#                     p     q
#                  e1   r     e4
#                     e2 e3
#
# then a subscription with a service path of '/' won't catch any entities
# at all whereas one with a service path of '/p' will consider changes to
# e1 but not e2 nor e3.


def create_subscriptions():
    print(
        f"Creating catch-all {TENANT} entities subscription for QuantumLeap.")
    print(
        f"Creating catch-all {TENANT} entities subscription for Roughnator.")

    man = SubMan()
    orion_subs = man.create_subscriptions()
    formatted = json.dumps(orion_subs, indent=4)

    print("Current subscriptions in Orion:")
    print(formatted)