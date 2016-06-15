// Copyright (c) 2010-2015 Quadralay Corporation.  All rights reserved.
//
// ePublisher 2015.1
//
// Validated with JSLint <http://www.jslint.com/>
//

/*jslint maxerr: 50, indent: 4 */
/*global window */
/*global Browser */
/*global Message */
/*global Highlight */
/*global Parcels */
/*global SearchClient */


// Page
//

var Page = {
    'window': window,
    'onload_handled': false,
    'loading': false,
    'height': 0,
    'socialized': false
};

Page.KnownParcelURL = function (param_url) {
    'use strict';

    var result;

    result = Parcels.KnownParcelURL(Page.connect_info.parcel_prefixes, param_url);

    return result;
};

Page.KnownParcelBaggageURL = function (param_url) {
    'use strict';

    var result;

    result = Parcels.KnownParcelBaggageURL(Page.connect_info.parcel_prefixes, param_url);

    return result;
};

Page.BackToTop = function () {
    'use strict';

    var data;

    // Scroll page to desired position
    //
    Page.window.scrollTo(0, 0);

    // Request parent window to scroll to the desired position
    //
    data = {
        'action': 'back_to_top'
    };
    Message.Post(Page.window.parent, data, Page.window);
};

Page.HandleToolbarLink = function (param_link) {
    'use strict';

    var result, behavior, data;

    result = true;

    if (typeof param_link.className === 'string') {
        // Determine handlers for button
        //
        for (behavior in Page.connect_info.button_behaviors) {
            if (typeof Page.connect_info.button_behaviors[behavior] === 'boolean') {
                if (Browser.ContainsClass(param_link.className, behavior)) {
                    // Invoke handler
                    //
                    data = {
                        'action': 'handle_toolbar_link',
                        'behavior': behavior
                    };
                    Message.Post(Page.window.parent, data, Page.window);

                    result = false;
                    break;
                }
            }
        }
    }

    return result;
};

Page.HandleInterceptLink = function (param_link) {
    'use strict';

    var result, image_src, resolved_image_src, data;

    result = Page.HandleToolbarLink(param_link);
    if (result === true) {
        if (Browser.GetAttribute(param_link, 'wwx:original-href') !== null) {
            // Resolve path to full-size image
            //
            image_src = Browser.GetAttribute(param_link, 'wwx:original-href');
            resolved_image_src = Browser.ResolveURL(Page.window.location.href, image_src);

            // Display image
            //
            data = {
                'action': 'display_image',
                'href': param_link.href,
                'src': resolved_image_src,
                'width': parseInt(Browser.GetAttribute(param_link, 'wwx:original-width'), 10),
                'height': parseInt(Browser.GetAttribute(param_link, 'wwx:original-height'), 10)
            };
            Message.Post(Page.window.parent, data, Page.window);

            // Prevent default link behavior
            //
            result = false;
        } else {
            // Standard link
            //
            if (Browser.ContainsClass(param_link.className, 'ww_behavior_back_to_top')) {
                // Back to top
                //
                Page.BackToTop();

                // Prevent default link behavior
                //
                result = false;
            }
            if ((param_link.href !== undefined) && (param_link.href !== null) && (param_link.href !== '')) {
                // Display link via default behavior
                //
                result = true;

                // Cancel event bubbling
                //
                event.cancelBubble = true;
                if (event.stopPropagation) {
                    event.stopPropagation();
                }
            }
        }
    }

    return result;
};

Page.InterceptLink = function (param_event) {
    'use strict';

    var result;

    // PDF?
    //
    if (Browser.ContainsClass(this.className, 'ww_behavior_pdf')) {
        // Process normally
        //
        result = true;
    } else {
        // Process event
        //
        result = Page.HandleInterceptLink(this);
    }

    return result;
};

Page.UpdateAnchors = function (param_document) {
    'use strict';

    var index, link, message, mailto;

    if (Page.anchors_updated === undefined) {
        Page.anchors_updated = true;

        for (index = param_document.links.length - 1; index >= 0; index -= 1) {
            link = param_document.links[index];

            // Update targets
            //
            if (Browser.ContainsClass(link.className, 'ww_behavior_email')) {
                // Create email link
                //
                message = Page.connect_info.email_message.replace('$Location;', Page.window.location.href);
                if (Page.window.navigator.userAgent.indexOf('MSIE') !== -1) {
                    message = message.replace('#', '%23');
                }
                mailto = 'mailto:' + Page.connect_info.email + '?subject=' + encodeURIComponent(message) + '&body=' + encodeURIComponent(message);
                link.href = mailto;
            } else if (Browser.SameHierarchy(Page.connect_info.base_url, link.href)) {
                // Verify parcel is known
                //
                if (Page.KnownParcelURL(link.href)) {
                    // Parcel is known
                    //
                    link.onclick = Page.InterceptLink;
                } else {
                    // Unknown parcel, kill link
                    //
                    Browser.RemoveAttribute(link, 'href', '');
                }
            } else {
                // Link to external (non-parcel) content
                //

                // Assign window target if not already defined
                //
                if ((link.target === undefined) || (link.target === null) || (link.target === '')) {
                    // Replace current window
                    //
                    link.target = Page.connect_info.target;
                }
            }
        }

        // On click handlers for Mini-TOC
        //
        Browser.ApplyToChildElementsWithTagName(Page.window.document.body, 'div', function (param_div_element) {
            var decorate_onclick;

            // Mini-TOC entry?
            //
            decorate_onclick = false;
            if (Browser.ContainsClass(param_div_element.className, 'WebWorks_MiniTOC_Entry')) {
                decorate_onclick = true;
            }

            if (decorate_onclick) {
                // Add onclick to all parent elements of the link
                //
                Browser.ApplyToChildElementsWithTagName(param_div_element, 'a', function (param_anchor_element) {
                    var parent_element;

                    parent_element = param_anchor_element;
                    while (parent_element !== param_div_element.parentNode) {
                        parent_element = parent_element.parentNode;
                        parent_element.onclick = Page.HandleOnClickAsNestedAnchor;
                    }
                });
            }
        });

        // On click handlers for Related Topics
        //
        Browser.ApplyToChildElementsWithTagName(Page.window.document.body, 'dd', function (param_dd_element) {
            var decorate_onclick;

            // Related Topic entry?
            //
            decorate_onclick = false;
            if (Browser.ContainsClass(param_dd_element.className, 'Related_Topics_Entry')) {
                decorate_onclick = true;
            }

            if (decorate_onclick) {
                // Add onclick to all parent elements of the link
                //
                Browser.ApplyToChildElementsWithTagName(param_dd_element, 'a', function (param_anchor_element) {
                    var parent_element;

                    parent_element = param_anchor_element;
                    while (parent_element !== param_dd_element.parentNode) {
                        parent_element = parent_element.parentNode;
                        parent_element.onclick = Page.HandleOnClickAsNestedAnchor;
                    }
                });
            }
        });
    }
};

Page.GetPrevNext = function (param_document, param_prevnext) {
    'use strict';

    var result, link_href;

    try {
        link_href = Browser.GetLinkRelHREF(param_document, param_prevnext);
        if ((link_href !== '') && (link_href !== '#')) {
            // Ensure link is fully resolved
            // (workaround IE's compatibility view)
            //
            result = Browser.ResolveURL(param_document.location.href, link_href);
        }
    } catch (ignore) {
        // Ignore all errors!
        //
    }

    return result;
};

Page.SearchQueryHighlight = function (param_search_query) {
    'use strict';

    var expressions, nodes_to_expand, node_to_expand, dropdown_element;

    // Remove highlights
    //
    Highlight.RemoveFromDocument(Page.window.document, 'Search_Result_Highlight');

    // Highlight words
    //
    if (param_search_query !== undefined) {
        // Convert search query into expressions
        //
        expressions = SearchClient.SearchQueryToExpressions(param_search_query);

        // Track nodes for possible expansion
        //
        nodes_to_expand = [];

        // Apply highlights
        //
        Highlight.ApplyToDocument(Page.window.document, 'Search_Result_Highlight', expressions, function (param_node) {
            nodes_to_expand.push(param_node);
        });

        // Expand nodes
        //
        while (nodes_to_expand.length > 0) {
            node_to_expand = nodes_to_expand.pop();

            // Inside dropdown?
            //
            dropdown_element = Page.InsideCollapsedDropdown(node_to_expand);
            if (dropdown_element !== undefined) {
                Page.RevealDropdownContent(dropdown_element);
            }
        }
    }
};

Page.InsideCollapsedDropdown = function (param_node) {
    'use strict';

    var result, current_node;

    result = undefined;
    current_node = param_node;
    while ((result === undefined) && (current_node !== undefined) &&  (current_node !== null)) {
        if (Browser.ContainsClass(current_node.className, 'ww_skin_page_dropdown_div_collapsed')) {
            result = current_node;
        }

        current_node = current_node.parentNode;
    }

    return result;
};

Page.RevealDropdownContent = function (param_dropdown_element) {
    'use strict';

    var dropdown_id_suffix_index, dropdown_id;

    // Expand dropdown
    //
    dropdown_id_suffix_index = param_dropdown_element.id.lastIndexOf(':dd');
    if (dropdown_id_suffix_index === (param_dropdown_element.id.length - 3)) {
        dropdown_id = param_dropdown_element.id.substring(0, dropdown_id_suffix_index);
        WebWorks_ToggleDIV(dropdown_id);
    }
};

Page.Listen = function (param_event) {
    'use strict';

    if (Page.dispatch === undefined) {
        Page.dispatch = {
            'get_page_size': function (param_data) {
                var content_widthheight, data;

                // Update page height within tolerance
                //
                content_widthheight = Browser.GetWindowContentWidthHeight(Page.window);
                if ((content_widthheight.height > Page.height) && (content_widthheight.height < (Page.height + Page.connect_info.tolerance))) {
                    content_widthheight.height = Page.height;
                } else {
                    Page.height = content_widthheight.height;
                }

                data = {
                    'action': 'page_size',
                    'dimensions': content_widthheight,
                    'stage': param_data.stage
                };
                Message.Post(Page.window.parent, data, Page.window);
            },
            'update_hash': function (param_data) {
                var data;

                // Update hash
                //
                Page.window.document.location.hash = param_data.hash;
                Page.HashChanged();

                // Page bookkeeping
                //
                data = {
                    'action': 'page_bookkeeping',
                    'href': Page.window.document.location.href,
                    'hash': Page.window.document.location.hash
                };
                Message.Post(Page.window.parent, data, Page.window);
            },
            'update_anchors': function (param_data) {
                Page.connect_info = param_data;
                Page.UpdateAnchors(Page.window.document);
            },
            'page_set_max_width': function (param_data) {
                var data;

                // Set max width and overflow
                //
                Page.window.document.body.style.maxWidth = param_data.max_width;
                if (Page.css_rule_overflow !== undefined) {
                    Page.css_rule_overflow.style.overflowX = param_data.overflow;
                }

                // Notify
                //
                data = {
                    'action': 'notify_page_max_width_set'
                };
                Message.Post(Page.window.parent, data, Page.window);
            },
            'ww_behavior_print': function (param_data) {
                Page.window.print();
            },
            'ww_behavior_pdf': function (param_data) {
                var pdf_link, links, index, link, data;

                // Find PDF link
                //
                pdf_link = null;
                links = Page.window.document.body.getElementsByTagName('a');
                for (index = 0; index < links.length; index += 1) {
                    link = links[index];

                    if ((Browser.ContainsClass(link.className, 'ww_behavior_pdf')) && (link.href !== undefined) && (link.href.length > 0)) {
                        // Found our link!
                        //
                        pdf_link = link;
                        break;
                    }
                }

                // PDF link found?
                //
                if (pdf_link !== null) {
                    // Display link
                    //
                    data = {
                        'action': 'display_link',
                        'href': pdf_link.href,
                        'target': pdf_link.target
                    };
                    Message.Post(Page.window.parent, data, Page.window);
                }
            },
            'page_socialize': function (param_data) {
                var social_links_div, twitter_anchor, twitter_href, twitter_span, twitter_iframe, facebook_anchor, facebook_href, facebook_span, facebook_iframe, linkedin_anchor, linkedin_href, linkedin_span, linkedin_script, first_script, google_anchor, google_href, google_span, google_script, disqus_div, disqus_script;

                // Handle file protocol
                //
                if ((!Page.socialized) && (Page.window.document.location.protocol !== 'file:')) {
                    // Display social tools
                    //
                    social_links_div = Page.window.document.getElementById('social_links');
                    if (social_links_div !== null) {
                        social_links_div.style.display = 'inline-block';
                    }

                    // Twitter
                    //
                    if (social_links_div !== null) {
                        twitter_anchor = Page.window.document.getElementById('social_twitter');
                        if (twitter_anchor !== null) {
                            twitter_href = 'https://twitter.com/intent/tweet?source=webclient&url=' + encodeURI(Page.window.document.location.href);
                            twitter_anchor.href = twitter_href;
                        }
                    } else {
                        twitter_span = Page.window.document.getElementById('social_twitter');
                        if (twitter_span !== null) {
                            twitter_iframe = Browser.FirstChildElementWithTagName(twitter_span, 'iframe');
                            if (twitter_iframe !== null) {
                                twitter_iframe.contentWindow.location.replace('http://platform.twitter.com/widgets/tweet_button.html?lang=en&count=horizontal&url=' + encodeURI(Page.window.document.location.href));
                            }
                        }
                    }

                    // FaceBook Like
                    //
                    if (social_links_div !== null) {
                        facebook_anchor = Page.window.document.getElementById('social_facebook_like');
                        if (facebook_anchor !== null) {
                            facebook_href = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURI(Page.window.document.location.href);
                            facebook_anchor.href = facebook_href;
                        }
                    } else {
                        // FaceBook Like
                        //
                        facebook_span = Page.window.document.getElementById('social_facebook_like');
                        if (facebook_span !== null) {
                            facebook_iframe = Browser.FirstChildElementWithTagName(facebook_span, 'iframe');
                            if (facebook_iframe !== null) {
                                facebook_iframe.contentWindow.location.replace('http://www.facebook.com/plugins/like.php?layout=button_count&show_faces=false&action=like&colorscheme=light&width=90&height=20&href=' + encodeURI(Page.window.document.location.href));
                            }
                        }
                    }

                    // LinkedIn Share
                    //
                    if (social_links_div !== null) {
                        linkedin_anchor = Page.window.document.getElementById('social_linkedin');
                        if (linkedin_anchor !== null) {
                            linkedin_href = 'https://www.linkedin.com/shareArticle?url=' + encodeURI(Page.window.document.location.href);
                            linkedin_anchor.href = linkedin_href;
                        }
                    } else {
                        linkedin_span = Page.window.document.getElementById('social_linkedin');
                        if (linkedin_span !== null) {
                            linkedin_span.style.display = 'inline-block';
                            linkedin_script = Page.window.document.createElement('script');
                            linkedin_script.type = 'text/javascript';
                            linkedin_script.async = true;
                            linkedin_script.src = '//platform.linkedin.com/in.js';
                            first_script = Page.window.document.getElementsByTagName('script')[0];
                            first_script.parentNode.insertBefore(linkedin_script, first_script);
                        }
                    }

                    // Google +1
                    //
                    if (social_links_div !== null) {
                        google_anchor = Page.window.document.getElementById('social_google_plus1');
                        if (google_anchor !== null) {
                            google_href = 'https://plus.google.com/share?url=' + encodeURI(Page.window.document.location.href);
                            google_anchor.href = google_href;
                        }
                    } else {
                        // Google +1
                        //
                        google_span = Page.window.document.getElementById('social_google_plus1');
                        if (google_span !== null) {
                            google_script = Page.window.document.createElement('script');
                            google_script.type = 'text/javascript';
                            google_script.async = true;
                            google_script.src = 'https://apis.google.com/js/plusone.js';
                            first_script = Page.window.document.getElementsByTagName('script')[0];
                            first_script.parentNode.insertBefore(google_script, first_script);
                        }
                    }

                    // Disqus
                    //
                    if (param_data.disqus_id.length > 0) {
                        disqus_div = Page.window.document.getElementById('disqus_thread');
                        if (disqus_div !== null) {
                            disqus_script = Page.window.document.createElement('script');
                            disqus_script.type = 'text/javascript';
                            disqus_script.async = true;
                            disqus_script.src = 'http://' + param_data.disqus_id + '.disqus.com/embed.js';
                            disqus_div.parentNode.appendChild(disqus_script);
                        }
                    }

                    Page.socialized = true;
                }
            },
            'page_globalize': function (param_data) {
                var google_translate_div, google_translate_script;

                // Google Translation
                //
                google_translate_div = Page.window.document.getElementById('google_translate_element');
                if (google_translate_div !== null) {
                    google_translate_script = Page.window.document.createElement('script');
                    google_translate_script.type = 'text/javascript';
                    google_translate_script.async = true;
                    google_translate_script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
                    google_translate_div.appendChild(google_translate_script);
                }
            },
            'page_search_query_highlight': function (param_data) {
                Page.SearchQueryHighlight(param_data.search_query);
            },
            'resize_complete': function (param_data) {
                // Scroll to correct position if loading the page
                //
                if (Page.loading) {
                    // Invoke hash changed handler
                    //
                    Page.HashChanged();
                }

                // No longer loading a page
                //
                Page.loading = false;
            }
        };
    }

    try {
        // Dispatch
        //
        Page.dispatch[param_event.data.action](param_event.data);
    } catch (ignore) {
        // Keep on rolling
        //
    }
};

Page.ScrollElementIntoView = function (param_element) {
    'use strict';

    var dropdown_element, scroll_position, data;

    // Inside dropdown?
    //
    dropdown_element = Page.InsideCollapsedDropdown(param_element);
    if (dropdown_element !== undefined) {
        Page.RevealDropdownContent(dropdown_element);
    }

    // Try easy way
    //
    if (param_element.scrollIntoView !== undefined) {
        param_element.scrollIntoView();
    }

    // Unable to know if easy way worked, so try the hard way as well
    // Needed for Google Chrome
    //

    // Determine scroll position
    //
    scroll_position = Browser.GetElementScrollPosition(param_element);

    // Request parent window to scroll to the desired position
    //
    data = {
        'action': 'page_scroll_view',
        'left': scroll_position.left,
        'top': scroll_position.top
    };
    Message.Post(Page.window.parent, data, Page.window);
};

Page.ContentChanged = function () {
    'use strict';

    var data;

    data = {
        'action': 'page_content_changed'
    };
    Message.Post(Page.window.parent, data, Page.window);

    return true;
};

Page.HashChanged = function () {
    'use strict';

    var target_element_id, target_element;

    // Locate target element and update scroll position
    //
    target_element_id = (Page.window.location.hash.length > 1) ? Page.window.location.hash.substring(1) : '';
    if (target_element_id.length > 0) {
        target_element = Page.window.document.getElementById(target_element_id);
        if (target_element !== null) {
            Page.ScrollElementIntoView(target_element);
        }
    }

    return true;
};

Page.HandleOnClickAsNestedAnchor = function (param_event) {
    'use strict';

    var event, anchor_elements, data, anchor_element;

    // Access event
    //
    event = param_event || window.event;

    // Cancel event bubbling
    //
    event.cancelBubble = true;
    if (event.stopPropagation) {
        event.stopPropagation();
    }

    // Locate anchor and process link
    //
    anchor_elements = this.getElementsByTagName('a');
    if (anchor_elements.length > 0) {
        // Display link
        //
        anchor_element = anchor_elements[0];
        if ((anchor_element.href !== undefined) && (anchor_element.href !== null) && (anchor_element.href !== '')) {
            data = {
                'action': 'display_link',
                'href': anchor_element.href,
                'target': anchor_element.target
            };
            Message.Post(Page.window.parent, data, Page.window);
        }
    }
};

Page.OnUnload = function () {
    'use strict';

    var data;

    // Notify parent
    //
    data = {
        'action': 'page_unload'
    };
    Message.Post(Page.window.parent, data, Page.window);
};

Page.OnLoad = function (param_event_or_redirect_url) {
    'use strict';

    var redirect_url, page_hash, skin_stylesheet, stylesheets_index, stylesheet, css_rules, css_rules_index, css_rule, css_rule_selector_text, stylesheet_element, back_to_top_element, data;

    if (Page.window === Page.window.top) {
        // Redirect
        //
        if ((param_event_or_redirect_url !== undefined) && (typeof param_event_or_redirect_url === 'string')) {
            redirect_url = param_event_or_redirect_url;
            if (Page.window.document.location.hash.length > 1) {
                // Sanitize and append it
                //
                page_hash = Page.window.document.location.hash.substring(1);
                page_hash = page_hash.replace(/[\\<>:;"']|%5C|%3C|%3E|%3A|%3B|%22|%27/gi, '');
                redirect_url += '#' + page_hash;
            }
            Page.window.document.location.replace(redirect_url);
        }
    } else if (!Page.onload_handled) {
        // Handle onload event only once
        //
        Page.onload_handled = true;

        // Track unload
        //
        Page.window.onunload = Page.OnUnload;

        // Setup for listening
        //
        Message.Listen(Page.window, function (param_event) {
            Page.Listen(param_event);
        });

        // Track document content changes
        //
        Browser.TrackDocumentChanges(Page.window, Page.window.document, Page.ContentChanged);

        // Track hash changes
        //
        if ('onhashchange' in Page.window) {
            // Events are so nice!
            //
            Page.window.onhashchange = Page.HashChanged;
        } else {
            // Poll
            //
            Page.hash = Page.window.location.hash.substring(1);
            Page.poll_onhashchange = function () {
                var hash;

                hash = Page.window.location.hash.substring(1);
                if (hash !== Page.hash) {
                    Page.hash = hash;

                    Page.HashChanged();
                }

                Page.window.setTimeout(Page.poll_onhashchange, 100);
            };
            Page.window.setTimeout(Page.poll_onhashchange, 1);
        }

        // Find overflow CSS rule
        //
        Page.css_rule_overflow = undefined;
        try {
            // Locate skin stylesheet
            //
            skin_stylesheet = undefined;
            for (stylesheets_index = 0; stylesheets_index < Page.window.document.styleSheets.length; stylesheets_index += 1) {
                stylesheet = window.document.styleSheets[stylesheets_index];

                if ((typeof stylesheet.href === 'string') && (stylesheet.href.indexOf('skin.css') >= 0)) {
                    skin_stylesheet = stylesheet;
                    break;
                }
            }

            // Found skin stylesheet?
            //
            if (skin_stylesheet !== undefined) {
                css_rules = skin_stylesheet.cssRules;
                if (css_rules === undefined) {
                    css_rules = skin_stylesheet.rules;
                }

                // Google Chrome bug?
                //
                // http://code.google.com/p/chromium/issues/detail?id=49001
                // If the stylesheet and the HTML are both on local disk, this bug occurs
                // (i.e. you get a null stylesheet from document.styleSheets).
                //
                if ((css_rules === undefined) || (css_rules === null)) {
                    // Dynamically create a new stylesheet
                    //
                    stylesheet_element = Page.window.document.createElement('style');
                    stylesheet_element.type = 'text/css';
                    Page.window.document.head.appendChild(stylesheet_element);
                    stylesheet = window.document.styleSheets[Page.window.document.styleSheets.length - 1];
                    stylesheet.insertRule('.ww_skin_page_overflow { overflow-x: auto; overflow-y: hidden; }', stylesheet.cssRules.length);
                    css_rules = stylesheet.cssRules;
                }

                // Find overflow rule
                //
                for (css_rules_index = 0; css_rules_index < css_rules.length; css_rules_index += 1) {
                    css_rule = css_rules[css_rules_index];
                    css_rule_selector_text = css_rule.selectorText.toLowerCase();  // Handle IE 7,8

                    if (css_rule_selector_text === '.ww_skin_page_overflow') {
                        Page.css_rule_overflow = css_rule;
                    }
                }
            }
        } catch (ignore) {
            // Live without it
            //
        }

        // Hook up back to top
        //
        back_to_top_element = Page.window.document.getElementById('back_to_top');
        if (back_to_top_element !== null) {
            back_to_top_element.onclick = Page.BackToTop;
        }

        // Notify parent
        //
        Page.loading = true;
        data = {
            'action': 'page_load',
            'dimensions': Browser.GetWindowContentWidthHeight(Page.window),
            'id': Page.window.document.body.id,
            'title': Page.window.document.title,
            'href': Page.window.document.location.href,
            'hash': Page.window.document.location.hash,
            'Prev': Page.GetPrevNext(Page.window.document, 'Prev'),
            'Next': Page.GetPrevNext(Page.window.document, 'Next')
        };
        Message.Post(Page.window.parent, data, Page.window);
    }
};


// Dropdowns
//

function WebWorks_WriteArrow(param_id, param_expanded) {
    'use strict';

    var arrow_class, dropdown_arrow_id;

    arrow_class = (param_expanded ? 'ww_skin_page_dropdown_arrow_expanded' : 'ww_skin_page_dropdown_arrow_collapsed');
    dropdown_arrow_id = param_id + ":dd:arrow";
    window.document.write('&#160;<span id="' + dropdown_arrow_id + '" class="ww_skin ww_skin_dropdown_arrow ' + arrow_class + '">&#160;</span>');
}

function WebWorks_WriteDIVOpen(param_id, param_expanded) {
    'use strict';

    var dropdown_div_class, dropdown_div_id;

    dropdown_div_class = (param_expanded ? 'ww_skin_page_dropdown_div_expanded' : 'ww_skin_page_dropdown_div_collapsed');
    dropdown_div_id = param_id + ":dd";
    window.document.write('<div id="' + dropdown_div_id + '" class="' + dropdown_div_class + '">');
}

function WebWorks_WriteDIVClose() {
    'use strict';

    window.document.write('</div>');
}

function WebWorks_ToggleDIV(param_id) {
    'use strict';

    var dropdown_div_id, dropdown_arrow_id, dropdown_div, dropdown_a, dropdown_div_className, dropdown_a_className;

    dropdown_div_id = param_id + ":dd";
    dropdown_arrow_id = param_id + ":dd:arrow";

    dropdown_div = window.document.getElementById(dropdown_div_id);
    dropdown_a = window.document.getElementById(dropdown_arrow_id);
    if ((dropdown_div !== null) && (dropdown_a !== null)) {
        dropdown_div_className = dropdown_div.className.replace('ww_skin_page_dropdown_div_expanded', '').replace('ww_skin_page_dropdown_div_collapsed', '');
        dropdown_a_className = dropdown_a.className.replace(' ww_skin_page_dropdown_arrow_expanded', '').replace(' ww_skin_page_dropdown_arrow_collapsed', '');
        if (dropdown_div.className.indexOf('ww_skin_page_dropdown_div_expanded') >= 0) {
            dropdown_div_className += 'ww_skin_page_dropdown_div_collapsed';
            dropdown_a_className += ' ww_skin_page_dropdown_arrow_collapsed';
        } else {
            dropdown_div_className += 'ww_skin_page_dropdown_div_expanded';
            dropdown_a_className += ' ww_skin_page_dropdown_arrow_expanded';
        }
        dropdown_div.className = dropdown_div_className;
        dropdown_a.className = dropdown_a_className;
    }

    Page.ContentChanged();

    return false;
}


// Start running as soon as possible
//
if (window.addEventListener !== undefined) {
    window.addEventListener('load', Page.OnLoad, false);
} else if (window.attachEvent !== undefined) {
    window.attachEvent('onload', Page.OnLoad);
}
