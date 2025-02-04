// Function to switch between matches and players sections
function switchPage(page) {
    const matchesSection = document.getElementById('matches-section');
    const playersSection = document.getElementById('players-section');
    
    if (page === 'players') {
        // Hide matches section, show players section
        matchesSection.style.display = 'none';
        playersSection.style.display = 'block';

        loadPlayers();  // Load players when switching to players section
        loadGoalies();  // Load goalies when switching to players section
    } else {
        // Hide players section, show matches section
        matchesSection.style.display = 'block';
        playersSection.style.display = 'none';

        loadMatches();  // Load matches when switching to matches section
    }
}

// Call the switchPage function to ensure the page loads with matches first
window.onload = function() {
    switchPage('matches');
};

// Function to load the match data (same as before)
function loadMatches() {
    fetch('/static/matches.json')
        .then(response => response.json())
        .then(matches => {
            const matchesList = document.getElementById('matches-list');
            matchesList.innerHTML = '';  // Clear the previous matches

            if (matches.length === 0) {
                matchesList.innerHTML = "<p>No matches available.</p>";
                return;
            }

            matches.forEach(match => {
                const matchElement = document.createElement('div');
                matchElement.classList.add('match');
                matchElement.innerHTML = `
                    <div class="match-header">
                        <div class="team-info">
                            <img src="${match.homeLogo}" alt="${match.homeTeam} logo" class="team-logo">
                            <span class="team">${match.homeTeam} ${match.score.split('-')[0].trim()} - ${match.score.split('-')[1].trim()} ${match.awayTeam}</span>
                            <img src="${match.awayLogo}" alt="${match.awayTeam} logo" class="team-logo">
                        </div>
                        <span class="status">${match.status}</span>
                    </div>
                `;
                matchesList.appendChild(matchElement);
            });
        })
        .catch(error => {
            console.error("Error loading JSON:", error);
        });
}

// Function to load players data into the players container
function loadPlayers() {
    fetch('/static/finnish_players.json')
        .then(response => response.json())
        .then(data => {
            const playersContainer = document.getElementById('players-container');
            const goaliesContainer = document.getElementById('goalies-container');
            playersContainer.innerHTML = '';  // Clear the previous player data
            goaliesContainer.innerHTML = '';  // Clear the previous goalie data

            // Check if the player data is empty
            if (!data.forwards_and_defense.length && !data.goalies.length) {
                playersContainer.innerHTML = "<p>No players available.</p>";
                goaliesContainer.innerHTML = "<p>No goalies available.</p>";
                return;
            }

            // Call the function to load player data into the table
            loadPlayerTable(data);
            loadGoalieTable(data);  // Load goalies into a separate table
        })
        .catch(error => {
            console.error('Error loading player data:', error);
        });
}

// Function to load players into the table
function loadPlayerTable(data) {
    const playersTable = document.getElementById('players-container');
    const table = document.createElement('table');
    
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = `
        <th>Photo</th>
        <th>Name</th>
        <th>Team</th>
        <th>Goals</th>
        <th>Assists</th>
        <th>Points</th>
        <th>+/-</th>
        <th>TOI</th>
    `;
    table.appendChild(headerRow);

    data.forwards_and_defense.forEach(player => {
        const row = createPlayerRow(player);
        table.appendChild(row);
    });

    playersTable.appendChild(table);
}

// Function to load goalies into a separate table
function loadGoalieTable(data) {
    const goaliesContainer = document.getElementById('goalies-container');
    const goalieTable = document.createElement('table');
    
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = `
        <th>Photo</th>
        <th>Name</th>
        <th>Team</th>
        <th>Saves</th>
        <th>Shots Against</th>
        <th>Save %</th>
        <th>TOI</th>
    `;
    goalieTable.appendChild(headerRow);

    data.goalies.forEach(goalie => {
        const row = createGoalieRow(goalie);
        goalieTable.appendChild(row);
    });

    goaliesContainer.appendChild(goalieTable);
}

// Function to create a player row in the table
function createPlayerRow(player) {
    const row = document.createElement('tr');

    // Player photo cell
    const photoCell = document.createElement('td');
    const playerPhoto = document.createElement('img');
    playerPhoto.classList.add('player-photo');
    playerPhoto.src = player.photo_link;
    playerPhoto.alt = `${player.name} photo`;
    photoCell.appendChild(playerPhoto);
    
    // Player name cell
    const nameCell = document.createElement('td');
    nameCell.textContent = player.name;

    // Team and Number cell (combined)
    const teamNumberCell = document.createElement('td');
    teamNumberCell.textContent = `${player.team}  #${player.sweater_number}`;

    // Player goals cell
    const goalsCell = document.createElement('td');
    goalsCell.textContent = player.goals;

    // Player assists cell
    const assistsCell = document.createElement('td');
    assistsCell.textContent = player.assists;

    // Player points cell
    const pointsCell = document.createElement('td');
    pointsCell.textContent = player.points;

    // Player +/− cell
    const plusMinusCell = document.createElement('td');
    plusMinusCell.textContent = player.plus_minus;

    // Player TOI (Time on Ice) cell
    const toiCell = document.createElement('td');
    toiCell.textContent = player.toi;

    // Append all cells to the row
    row.appendChild(photoCell);
    row.appendChild(nameCell);
    row.appendChild(teamNumberCell);
    row.appendChild(goalsCell);
    row.appendChild(assistsCell);
    row.appendChild(pointsCell);
    row.appendChild(plusMinusCell);
    row.appendChild(toiCell);

    return row;
}

// Function to create goalie row in the table
function createGoalieRow(goalie) {
    const row = document.createElement('tr');

    // Goalkeeper photo cell
    const photoCell = document.createElement('td');
    const goaliePhoto = document.createElement('img');
    goaliePhoto.classList.add('player-photo');
    goaliePhoto.src = goalie.photo_link;
    goaliePhoto.alt = `${goalie.name} photo`;
    photoCell.appendChild(goaliePhoto);

    // Goalkeeper name cell
    const nameCell = document.createElement('td');
    nameCell.textContent = goalie.name;

    // Team and Number cell (combined)
    const teamNumberCell = document.createElement('td');
    teamNumberCell.textContent = `${goalie.team}  #${goalie.sweater_number}`;

    // Goalkeeper saves cell
    const savesCell = document.createElement('td');
    savesCell.textContent = goalie.saves;

    // Shots against cell
    const shotsAgainstCell = document.createElement('td');
    shotsAgainstCell.textContent = goalie.shots_against;

    // Save percentage cell
    const savePercentageCell = document.createElement('td');
    savePercentageCell.textContent = goalie.save_pctg;

    // Goalkeeper TOI cell
    const toiCell = document.createElement('td');
    toiCell.textContent = goalie.toi;

    // Append all cells to the row
    row.appendChild(photoCell);
    row.appendChild(nameCell);
    row.appendChild(teamNumberCell);
    row.appendChild(savesCell);
    row.appendChild(shotsAgainstCell);
    row.appendChild(savePercentageCell);
    row.appendChild(toiCell);

    return row;
}
