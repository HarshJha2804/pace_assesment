// Dismiss alert boxes after a specified number of seconds
setTimeout(function () {
    var alerts = document.querySelectorAll('#alert-box');
    alerts.forEach(function (alert) {
        alert.remove();
    });
}, 5000); // 5000 milliseconds = 5 seconds

/*
Notification Module Start
===========================================================================================
*/


// Updating notification badge on notification count
function updateNotificationBadgeVisibility() {
    let notificationBadge = document.getElementById('notification-icon');
    if (notificationBadge) {
        notificationBadge = notificationBadge.nextElementSibling
        let notificationCount = parseInt(notificationBadge.innerHTML);

        if (notificationCount > 0) {
            notificationBadge.classList.remove('d-none');
        } else {
            notificationBadge.classList.add('d-none');
        }
    }
}


// Updating Notification icon on toggle
function UpdateNotificationIcon(notificationLink, notificationIcon) {
    let expanded = notificationLink.getAttribute('aria-expanded') === 'true';
    if (expanded) {
        notificationIcon.classList.add('ti-bell-filled')
        notificationIcon.classList.remove('ti-bell')
    } else {
        notificationIcon.classList.remove('ti-bell-filled')
        notificationIcon.classList.add('ti-bell')
    }
}

// On Notification toggle mark notifications as read!
function MarkNotificationsAsRead(notificationIcon) {
    let notificationCount = notificationIcon.nextElementSibling
    var xhr = new XMLHttpRequest();
    xhr.open('GET', notification_mark_all_as_read, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var responseData = JSON.parse(xhr.responseText);
                notificationCount.innerHTML = responseData.unread_count
                updateNotificationBadgeVisibility()
            } else {
                console.log('Error marking notifications as read:', xhr.statusText);
            }
        }
    };
    xhr.send();
}

// Fetching a read and unread notification list
function fetchNotificationsReadAndUnreadList() {
    fetch(notificationReadUnreadListUrl)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('notifications-container');
            const template = document.getElementById('notification-template');
            const clonedTemplate = template.cloneNode(true);

            // Removing all container child elements
            removeAllNotificationItem(container);

            data.forEach(notification => {
                let clone = clonedTemplate.cloneNode(true);
                clone.querySelector('.status-dot').classList.add('bg-' + notification.fields.level);
                clone.querySelector('.text-body').textContent = notification.fields.verb;
                clone.querySelector('.text-secondary').textContent = notification.fields.description || '';
                clone.querySelector('.text-muted').textContent = timeSince(notification.fields.timestamp);
                clone.querySelector('a').setAttribute('href', `/notification/${notification.pk}/`);
                container.appendChild(clone);
            });
            updateNotificationBadgeVisibility()
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}


up.on('up:fragment:inserted', function () {

    const notificationLink = document.getElementById('notification-link');
    const notificationIcon = document.getElementById('notification-icon');
    if (notificationLink && notificationIcon) {
        updateNotificationBadgeVisibility()
        notificationLink.addEventListener('click', function (event) {
            event.preventDefault();
            //Fetching a Read and Unread notification list.
            fetchNotificationsReadAndUnreadList()
            UpdateNotificationIcon(notificationLink, notificationIcon)
            MarkNotificationsAsRead(notificationIcon)
        });

        up.on('click', function (event) {
            if (!notificationLink.contains(event.target)){
                notificationLink.setAttribute('aria-expanded', 'false');
                UpdateNotificationIcon(notificationLink, notificationIcon);
            }
        });
    }
});



function timeSince(dateString) {
    const providedDate = new Date(dateString);
    const currentDate = new Date();
    let timeDifference = Math.floor((currentDate - providedDate) / 1000); // Convert milliseconds to seconds

    const intervals = [
        {label: 'day', seconds: 86400},
        {label: 'hour', seconds: 3600},
        {label: 'minute', seconds: 60}
    ];

    let result = intervals.reduce((acc, interval) => {
        const count = Math.floor(timeDifference / interval.seconds);
        if (count > 0) {
            acc += `${count} ${interval.label}${count > 1 ? 's' : ''} `;
            timeDifference -= count * interval.seconds;
        }
        return acc;
    }, '');

    return result ? `${result.trim()} ago` : 'just now';
}


function removeAllNotificationItem(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

/*
Notification Module End Here.
----------------------------------------------------------------------------------------------
 */

document.addEventListener("DOMContentLoaded", function () {
    var selects = document.querySelectorAll('select[data-searchable="true"]');

    if (window.TomSelect && selects.length > 0) {
        selects.forEach(function (select) {
            new window.TomSelect(select, {
                copyClassesToDropdown: false,
                dropdownClass: 'dropdown-menu ts-dropdown',
                optionClass: 'dropdown-item',
                controlInput: '<input>',
                render: {
                    item: function (data, escape) {
                        if (data.customProperties) {
                            return '<div><span class="dropdown-item-indicator">' + data.customProperties + '</span>' + escape(data.text) + '</div>';
                        }
                        return '<div>' + escape(data.text) + '</div>';
                    },
                    option: function (data, escape) {
                        if (data.customProperties) {
                            return '<div><span class="dropdown-item-indicator">' + data.customProperties + '</span>' + escape(data.text) + '</div>';
                        }
                        return '<div>' + escape(data.text) + '</div>';
                    },
                },
            });
        });
    }
});
