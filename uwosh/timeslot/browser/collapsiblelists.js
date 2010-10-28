
/*
 * This is really a ripoff of the collapsiblesections.js code that comes with plone.
 * But I really need nested lists which don't work very well with the way plone themes 
 * <dl> collapsible sections.
 *
 * This code expects you to set up your html like this.
 * <ul>
 *   <div>
 *     <li class="collapsibleListHeader>Outer Header</li>
 *     <ul class="collapsibleList collapsed">
 *       <div>
 *         <li class="collapsibleListHeader>Inner Header</li>
 *         <ul class="collapsibleList collapsed">
 *           <li>Inner list element 1</li>
 *           <li>Inner list element 2</li>
 *         </ul>
 *       </div>
 *     </ul> 
 *   </div>
 * </ul>
 *
 */

function activateCollapsibleLists() {
    jq('li.collapsibleListHeader').addClass('collapsed');
    jq('ul.collapsibleList').addClass('collapsed');

    jq('li.collapsibleListHeader').click(function() {
        var $sublist = jq(this).parent().find('ul.collapsibleList:first');
        if (!$sublist) { return true; }

        $sublist.toggleClass('collapsed')
                .toggleClass('expanded');

	jq(this).toggleClass('collapsed')
                .toggleClass('expanded');
      })
};

jq(activateCollapsibleLists);
