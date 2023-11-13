import List from './pages/List.js';
import Leaderboard from './pages/Leaderboard.js';
import ListPacks from './pages/ListPacks.js';
import Roulette from './pages/Roulette.js'

export default [
    { path: '/', component: List },
    { path: '/leaderboard', component: Leaderboard },
    { path: '/list-packs', component: ListPacks },
    { path: '/roulette', component: Roulette }
];
