$( document ).ready(function() {
    console.log( "ready!" );

    $.ajax({
        "url": "/state",
        "dataType": "text json",
        "success": function(data, status, xhr) {
            let state = $.parseJSON(data.state);
            console.log("state");
            console.log(state);

            updatePage(state);
        },
        "error": function(xhr, status, error) {
            console.error("error", xhr);
        }
    });
});

function updatePage(state) {
    updatePlayer($(".human"), state._players[0]);
    updatePlayer($(".bot"), state._players[1]);
}

function updatePlayer(sectionElement, player) {
    updateHand(1, sectionElement, player);
    updateHand(2, sectionElement, player);
}

function updateHand(hand, sectionElement, player) {
    let fingers = player._hands[hand-1].alive_fingers;
    $(".hands .hand:nth-child("+hand+")", sectionElement).text(fingers)
}