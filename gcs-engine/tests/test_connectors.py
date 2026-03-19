"""Tests for all GCS Engine data connectors."""
import pytest
import pandas as pd

from src.connectors.genesys_stub import GenesysConnector
from src.connectors.helpdesk_stub import HelpDeskConnector
from src.connectors.ukg_stub import UKGConnector
from src.connectors.wcs_stub import WCSConnector
from src.connectors.service_mix import ServiceMixConnector
from src.connectors.bead_data import BEADConnector


class TestGenesysConnector:
    def test_returns_dataframe_with_partner_id(self):
        df = GenesysConnector().get_data()
        assert isinstance(df, pd.DataFrame)
        assert "partner_id" in df.columns

    def test_has_30_rows(self):
        df = GenesysConnector().get_data()
        assert len(df) == 30

    def test_volume_growth_rate_range(self):
        df = GenesysConnector().get_data()
        assert df["volume_growth_rate"].min() >= -0.20
        assert df["volume_growth_rate"].max() <= 0.30


class TestHelpDeskConnector:
    def test_returns_dataframe_with_partner_id(self):
        df = HelpDeskConnector().get_data()
        assert isinstance(df, pd.DataFrame)
        assert "partner_id" in df.columns

    def test_has_30_rows(self):
        df = HelpDeskConnector().get_data()
        assert len(df) == 30

    def test_repeat_contact_rate_range(self):
        df = HelpDeskConnector().get_data()
        assert (df["repeat_contact_rate"] >= 0).all()
        assert (df["repeat_contact_rate"] <= 1).all()


class TestUKGConnector:
    def test_returns_dataframe_with_partner_id(self):
        df = UKGConnector().get_data()
        assert isinstance(df, pd.DataFrame)
        assert "partner_id" in df.columns

    def test_has_30_rows(self):
        df = UKGConnector().get_data()
        assert len(df) == 30

    def test_utilization_rate_range(self):
        df = UKGConnector().get_data()
        assert (df["utilization_rate"] >= 0).all()
        assert (df["utilization_rate"] <= 1).all()


class TestWCSConnector:
    def test_returns_dataframe_with_partner_id(self):
        df = WCSConnector().get_data()
        assert isinstance(df, pd.DataFrame)
        assert "partner_id" in df.columns

    def test_has_30_rows(self):
        df = WCSConnector().get_data()
        assert len(df) == 30

    def test_seasonal_variance_coeff_non_negative(self):
        df = WCSConnector().get_data()
        assert (df["seasonal_variance_coeff"] >= 0).all()


class TestServiceMixConnector:
    def test_returns_dataframe_with_partner_id(self):
        df = ServiceMixConnector().get_data()
        assert isinstance(df, pd.DataFrame)
        assert "partner_id" in df.columns

    def test_has_30_rows(self):
        df = ServiceMixConnector().get_data()
        assert len(df) == 30

    def test_all_partners_have_at_least_one_service(self):
        df = ServiceMixConnector().get_data()
        for _, row in df.iterrows():
            services = str(row["services"]).split(",")
            assert len(services) >= 1
            assert all(s.strip() != "" for s in services)


class TestBEADConnector:
    def test_returns_dataframe_with_required_columns(self):
        df = BEADConnector().get_data()
        assert isinstance(df, pd.DataFrame)
        assert "state" in df.columns
        assert "status" in df.columns
        assert "partner_ids" in df.columns

    def test_has_rows(self):
        df = BEADConnector().get_data()
        assert len(df) >= 10

    def test_valid_status_values(self):
        df = BEADConnector().get_data()
        valid_statuses = {"none", "approved", "imminent", "active"}
        assert set(df["status"].unique()).issubset(valid_statuses)
