# -*- coding: utf-8 -*-

import os


def hex_to_sikuli(s):
    number = ""

    for c in s:
        if c >= '0' and c <= '9':
            number += getattr(Key, 'NUM' + c)

        else:
            number += c

    return number


class Scenario(object):
    """
        Canopsis Test Scenario.
    """

    def __init__(self, *args, **kwargs):
        super(Scenario, self).__init__(*args, **kwargs)

    def run_steps(self):
        """
            Run all steps of the scenario.
        """

        self.step_login()

        self.step_create_view()
        self.step_edit_view()

        self.step_logout()

    def step_login(self):
        """
            Try to login using root:root.
        """

        # Find authentication popup
        find("screenshots/step1/login_popup.png")

        # Type login/password
        type(
            "screenshots/step1/login_popup_username.png",
            "root"
        )

        type(
            "screenshots/step1/login_popup_password.png",
            "root"
        )

        # And connect
        click("screenshots/step1/login_popup_connect.png")

        # Wait dashboard to be shown
        wait("screenshots/logo_canopsis.png")

    def step_create_view(self):
        """
            Create a new view named sikuli.
        """

        # Open "Build" menu
        click("screenshots/step2/menu_build.png")
        wait("screenshots/step2/menu_build_open.png")

        # Add new view
        click("screenshots/step2/new_view.png")
        wait("screenshots/step2/view_name_popup.png")

        # Type view's name
        type(
            "screenshots/step2/view_name_popup_field.png",
            "sikuli"
        )

        click("screenshots/step2/view_name_popup_ok.png")

        # Wait view to be shown
        wait("screenshots/step2/view_tab.png")

    def step_edit_view(self):
        """
            Add a diagram widget and a line graph widget to the view.
        """

        # View is in edit mode
        find("screenshots/step3/edit_popup.png")

        # Add a widget diagram
        dragDrop(
            "screenshots/step3/start_widget1.png",
            "screenshots/step3/end_widget1.png"
        )

        # Wait for the wizard
        wait("screenshots/step3/new_widget_wizard.png")

        # Add a new diagram
        click("screenshots/step3/wizard_select_diagram.png")
        wait("screenshots/step3/wizard_diagram_selected.png")

        # Select correct metrics
        click("screenshots/step3/wizard_choose_metrics.png")
        type(
            "screenshots/step3/wizard_search_metrics.png",
            "sikuli\n"
        )
        wait("screenshots/step3/wizard_metrics.png")

        doubleClick("screenshots/step3/wizard_metric_hosts_down.png")
        doubleClick("screenshots/step3/wizard_metric_hosts_up.png")

        # Save widget
        click("screenshots/step3/wizard_save.png")

        # Make sure our widget is shown
        wait("screenshots/step3/diagram_editmode.png")

        # Now, add a line graph
        dragDrop(
            "screenshots/step3/start_widget2.png",
            "screenshots/step3/end_widget2.png"
        )

        # Wait for the wizard
        wait("screenshots/step3/new_widget_wizard.png")

        # Add a new line graph
        click("screenshots/step3/wizard_select_linegraph.png")
        click("screenshots/step3/wizard_advanced_mode.png")
        wait("screenshots/step3/advanced_wizard_linegraph_selected.png")

        # Select correct metrics
        click("screenshots/step3/wizard_choose_metrics.png")
        type(
            "screenshots/step3/wizard_search_metrics.png",
            "sikuli\n"
        )
        wait("screenshots/step3/wizard_metrics.png")

        doubleClick("screenshots/step3/wizard_metric_services_down.png")
        doubleClick("screenshots/step3/wizard_metric_services_up.png")

        # Now customize metrics
        click("screenshots/step3/wizard_customize_metrics.png")
        wait("screenshots/step3/wizard_linegraph_customize_metrics.png")

        click("screenshots/step3/wizard_linegraph_cmetric_srv_down.png")
        type(
            "screenshots/step3/wizard_linegraph_custom_label.png",
            "Services Down"
        )

        paste(
            "screenshots/step3/wizard_linegraph_custom_curve_color.png",
            "AA4643"
        )

        click("screenshots/step3/wizard_linegraph_cmetric_srv_up.png")
        type(
            "screenshots/step3/wizard_linegraph_custom_label.png",
            "Services Up"
        )

        paste(
            "screenshots/step3/wizard_linegraph_custom_curve_color.png",
            "4572A7"
        )

        # Save widget
        click("screenshots/step3/wizard_save.png")

        # Make sure our widget is shown
        wait("screenshots/step3/linegraph_editmode.png")

        # Now, save the view
        click("screenshots/step3/view_save.png")
        wait("screenshots/step3/view_saved.png")

    def step_logout(self):
        """
            Logout from canopsis.
        """

        click("screenshots/logout.png")
        wait("screenshots/step1/login_popup.png")


if __name__ == "__main__":
    sc = Scenario()
    sc.run_steps()