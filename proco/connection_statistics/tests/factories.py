from factory import SubFactory
from factory import django as django_factory
from factory import fuzzy

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.locations.tests.factories import CountryFactory


class CountryWeeklyStatusFactory(django_factory.DjangoModelFactory):
    country = SubFactory(CountryFactory)
    year = fuzzy.FuzzyInteger(1900, 2200)
    week = fuzzy.FuzzyInteger(1, 53)
    schools_connected = fuzzy.FuzzyInteger(0, 1000)
    schools_connectivity_unknown = fuzzy.FuzzyInteger(0, 1000)
    schools_connectivity_no = fuzzy.FuzzyInteger(0, 1000)
    schools_connectivity_moderate = fuzzy.FuzzyInteger(0, 1000)
    schools_connectivity_good = fuzzy.FuzzyInteger(0, 1000)
    connectivity_speed = fuzzy.FuzzyDecimal(0.0, 100.0)
    integration_status = fuzzy.FuzzyChoice(dict(CountryWeeklyStatus.INTEGRATION_STATUS_TYPES).keys())
    avg_distance_school = fuzzy.FuzzyFloat(0.0, 1000.0)

    class Meta:
        model = CountryWeeklyStatus
