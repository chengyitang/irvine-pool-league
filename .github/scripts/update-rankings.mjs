import { Octokit } from '@octokit/rest';
import fs from 'fs';

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

const owner = process.env.GITHUB_REPOSITORY.split('/')[0];
const repo = process.env.GITHUB_REPOSITORY.split('/')[1];

async function getMatchResults() {
  try {
    // Get all comments from the specified issue
    const comments = await octokit.rest.issues.listComments({
      owner,
      repo,
      issue_number: process.env.ISSUE_NUMBER,
    });

    const matches = [];
    const matchPattern = /(\w+)\s*[>beat]\s*(\w+)/gi;

    comments.data.forEach(comment => {
      const body = comment.body;
      let match;
      
      while ((match = matchPattern.exec(body)) !== null) {
        matches.push({
          winner: match[1].trim(),
          loser: match[2].trim(),
          date: comment.created_at
        });
      }
    });

    return matches;
  } catch (error) {
    console.error('Error fetching comments:', error);
    return [];
  }
}

function calculateRankings(matches) {
  const players = {};
  
  matches.forEach(match => {
    // Initialize player data
    if (!players[match.winner]) {
      players[match.winner] = { win: 0, lose: 0 };
    }
    if (!players[match.loser]) {
      players[match.loser] = { win: 0, lose: 0 };
    }
    
    // Update win/loss records
    players[match.winner].win++;
    players[match.loser].lose++;
  });

  // Calculate win rate and sort
  const rankings = Object.entries(players).map(([name, stats]) => ({
    player: name,
    win: stats.win,
    lose: stats.lose,
    total: stats.win + stats.lose,
    winRate: stats.win / (stats.win + stats.lose)
  })).sort((a, b) => {
    if (b.winRate !== a.winRate) return b.winRate - a.winRate;
    return b.win - a.win;
  });

  return { rankings, matches };
}

function generateReadme(rankings, matches) {
  const matchHistory = matches.slice(-10).reverse(); // 最近10場比賽
  
  return `# irvine-pool-league 🎱

## Current Rankings

| Rank | Player | Wins | Losses | Total | Win Rate |
|------|--------|------|--------|-------|----------|
${rankings.map((player, index) => 
  `| ${index + 1} | ${player.player} | ${player.win} | ${player.lose} | ${player.total} | ${(player.winRate * 100).toFixed(1)}% |`
).join('\n')}

## Recent Match Records

| Date | Match | Winner |
|------|------|--------|
${matchHistory.map(match => 
  `| ${new Date(match.date).toLocaleDateString()} | ${match.winner} vs ${match.loser} | ${match.winner} |`
).join('\n')}

## How to record match results

1. Go to [Match Result Recording Issue](../../issues/1)
2. Enter the match results in the comment, format: \`PlayerA > PlayerB\` or \`PlayerA beat PlayerB\`
3. The system will automatically update the rankings

### Example:
- \`Thomas > Raymond\`
- \`Thomas beat Raymond\`
- \`Jerry > Kyle\`

---
*Rankings are updated automatically by GitHub Actions | Last updated: ${new Date().toLocaleString()}*
`;
}

async function main() {
  console.log('Start updating rankings...');
  
  const matches = await getMatchResults();
  console.log(`Found ${matches.length} match records`);
  
  if (matches.length === 0) {
    console.log('No match records found, skipping update');
    return;
  }
  
  const { rankings } = calculateRankings(matches);
  const readme = generateReadme(rankings, matches);
  
  fs.writeFileSync('README.md', readme);
  console.log('README.md updated');
}

main().catch(console.error);