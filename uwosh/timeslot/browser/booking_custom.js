jq(document).ready(function () {

        jq("input[name='submittedApplicationForAdvancedStanding']").attr('disabled', 'disabled');
        jq("input[name='slotSelection']:checked").parents('div.field tr').css('background-color', '#cef');

	/*Show the subfield on selection of this option*/
        jq("input[name='intendToApplyForAdvancedStanding']").click(function () { 
            if (this.value === "1") { 
                jq("input[name='submittedApplicationForAdvancedStanding']").enable();
                jq('#archetypes-fieldname-submittedApplicationForAdvancedStanding').fadeIn();
            } else {
                jq("input[name='submittedApplicationForAdvancedStanding']").attr('disabled', 'disabled');
                jq('#archetypes-fieldname-submittedApplicationForAdvancedStanding').fadeOut();
            }
        });

	/*Reproduce the page view if our field is already selected. This has come from
	 *a failed form submission. 
	 */
        var asField = jq("#intendToApplyForAdvancedStanding_1");
        if (asField.attr('checked')) {
	        asField.click();
        }

	/*Handle clicks within a row itself, rather than just the radio button*/
        jq("tr.timeslot").click(function () { 
	        var input = jq(this).find("input[name='slotSelection']");
	        if (input.length > 0) {
		        input.attr('checked', 'checked');
		        jq("tr.session-selected-True").removeClass('session-selected-True');
		        jq(this).addClass('session-selected-True');
	        }
        });

	/*Enable the buttons to change pages of the form*/
        function changePage(to_id) {
                location.hash = 'contactInfo'; 
                jq('a[href="#fieldsetlegend-' + to_id + '"]').click();
                return false;
            } 
        jq('#nextPageButton').click(function () {   
                                                    return changePage('extraInfo'); 
                                                });
        jq('#previousPageButton').click(function () { 
                                                    return changePage('slotSelection'); 
                                                });

        /*Prepare plone.app.jquerytools overlays for campus maps*/
        jq('a.link-session-map').filter(':not(.no-overlay)').prepOverlay({
                subtype: 'iframe',
                width: '80%',
                config: {mask: {color: '#000'}} 
	        });

	/*Prepare plone.app.jquerytools overlays for booking a user in (admin) or
	 * otherwise a user self-managing themselves
	 */
        jq('a#ehs-manage-bookings, a#ehs-admin-booking').prepOverlay({
                subtype: 'ajax',
                filter: '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info,dl.portalMessage.warning',
                closeselector: 'a#return-to-booking',
                formselector: 'form[name="ehs-manage-bookings"],form[name="ehs-book-user"]',
                noform: 'reload',
                config: {mask: {color: '#000'},
		    onBeforeClose: function () {
				        if (jq("div.overlay dl.portalMessage:contains('was cancelled successfully')").length === 1) {
					        window.location.href = window.location.href;
				        }
				    } 
		       } 
	        });

	/*Prepare plone.app.jquerytools overlays for selecting courses, showing
	 * booking results from a form submission or showing the reports page
	 */
        jq('#ehs-select-course, #ehs-booking-results-link, #contentview-ehs-reporting a').prepOverlay({
                subtype: 'ajax',
                filter: '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info,dl.portalMessage.warning',
                closeselector: 'a#return-to-booking,input[name="form.buttons.cancel"]',
                config: {mask: {color: '#000'}}
            });

        /*Show results if we have results from a session signup - this link isn't 
	 * visible otherwise so the code won't execute. */
        jq('#ehs-booking-results-link').click();

    });
