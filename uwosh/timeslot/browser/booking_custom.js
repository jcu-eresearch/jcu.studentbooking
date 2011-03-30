jq(document).ready(function () {

	/* Handle faceted navigation options on the page */
        faceted_navigation = function() {
                     var selected = [];
                     var not_selected = [];
                     var current_box = this.value;
                     jq('input.drilldown').each(function() {
                         if (this.checked) {
                             selected.push('.'+this.value);
                         } else if (current_box !== this.value) {
                             not_selected.push('.'+this.value);
                         }
                         });
                     selected = selected.join(',');
                     not_selected = not_selected.join(',');
                     
                     jq('tr.timeslot.'+this.value).not(not_selected).filter(selected || '*').toggle(this.checked);
                }    

        jq('input.drilldown').click(faceted_navigation);
	jq('#faculty_all').click(function() {
           jq('input.drilldown[value^="faculty"]:not(:checked)').attr('checked', true).each(faceted_navigation);
	});
	jq('#faculty_none').click(function() {
           jq('input.drilldown[value^="faculty"]:checked').attr('checked', false).each(faceted_navigation);
	});

	//Hide this field by default
        jq("input[name='submittedApplicationForAdvancedStanding']").attr('disabled', 'disabled');

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

	/*Reproduce the page view if coming from a failed form submission.*/
        var asField = jq("#intendToApplyForAdvancedStanding_1");
        if (asField.attr('checked')) {
	        asField.click();
        }
	//Highlight the row of a previous selection
        jq("input[name='slotSelection']:checked").parents('div.field tr').css('background-color', '#cef');
	/*Show the errors on the page in a suitable manner.  Jump to the first
	 * error on the page (try to change fieldset; jump to error)
	 */
	function fieldsetLegendForField(field) {
	    var fieldset_id = jq(field).parent('fieldset').attr('id');
	    return jq('a[href="#'+fieldset_id.replace('fieldset','fieldsetlegend')+'"]');
	}
	
	var errors = jq('div.field.error');
	if (errors.length > 0) {
	    errors.each(function() {
	    	    fieldsetLegendForField(this).css('color', 'red');
		    });
	    var first_error = errors.first();
	    fieldsetLegendForField(first_error).click();
	    location.hash = first_error.attr('id');
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

	/*Prepare plone.app.jquerytools overlays for booking a user in 
	 * (admin) or otherwise a user self-managing themselves
	 */
        jq('a#ehs-manage-bookings, \
	    a#ehs-admin-booking').prepOverlay({
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
        jq('#ehs-select-course, \
            #ehs-booking-results-link, \
            #contentview-ehs-reporting a').prepOverlay({
                subtype: 'ajax',
                filter: '#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info,dl.portalMessage.warning',
                closeselector: 'a#return-to-booking,input[name="form.buttons.cancel"]',
                config: {mask: {color: '#000'}}
            });

        /*Show results if we have results from a session signup - this link 
	 * isn't visible otherwise so the code won't execute. */
        jq('#ehs-booking-results-link').click();

    });
