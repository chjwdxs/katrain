from collections import deque
from typing import Dict, List, Optional, Set, Tuple


Coord = Tuple[int, int]


class FogOfWar:
    """
    Per-player fog-of-war manager.

    Rules implemented:
    - Visibility levels per player: 0 (none), 1 (visible but decays), 2 (fresh)
    - Start with full-board level 2 for both players
    - On a player's turn end (successful move or pass):
        1) Degrade that player's visibility (2->1, 1->0, 0 stays)
        2) From each own stone, do BFS up to view_distance with blocking at stones (include the blocking cell but don't continue through it), mark all reached cells as level 2
        3) Add all enemy stones currently in level>=1 to the player's exposed set (exposed persists until the stone is captured)
        4) Force all own stones' cells and all exposed enemy stones' cells to level 2
    - On illegal move attempt:
        - Apply the above steps, but in step 2 also add a BFS starting from the attempted coord that ignores blocking along paths
    """

    def __init__(self, game, view_distance: int = 3):
        self.game = game
        self.view_distance = max(0, int(view_distance))
        szx, szy = self.game.board_size
        self._szx, self._szy = szx, szy
        # levels[player][y][x] in {0,1,2}
        self.levels: Dict[str, List[List[int]]] = {
            "B": [[0 for _ in range(szx)] for _ in range(szy)],
            "W": [[0 for _ in range(szx)] for _ in range(szy)],
        }
        # exposed enemy stones per player (coordinates)
        self.exposed: Dict[str, Set[Coord]] = {"B": set(), "W": set()}

    def initialize_full_visibility(self):
        for p in ("B", "W"):
            for y in range(self._szy):
                row = self.levels[p][y]
                for x in range(self._szx):
                    row[x] = 2
            self.exposed[p].clear()

    def get_level(self, player: str, coord: Coord) -> int:
        x, y = coord
        if 0 <= x < self._szx and 0 <= y < self._szy:
            return self.levels[player][y][x]
        return 0

    def update_after_turn(self, player: str, attempted: Optional[Coord], success: bool):
        """
        Apply end-of-turn visibility update for `player`.
        attempted: coord that player tried to play (can be None for pass).
        success: True if move was legal and applied, False if it failed (illegal); on failure we also add an ignore-block BFS from attempted.
        """
        self._degrade(player)

        own_stones, enemy_stones, occupied = self._stones_state(player)

        # Step 2: BFS from each own stone (blocked)
        coverage: Set[Coord] = set()
        if own_stones:
            coverage |= self._bfs_from_sources(own_stones, self.view_distance, occupied, block_paths=True, include_sources=True)

        # Illegal move also explores from attempted coord ignoring blocking
        if not success and attempted is not None:
            coverage |= self._bfs_from_sources({attempted}, self.view_distance, occupied, block_paths=False, include_sources=True)

        # Mark explored coverage cells as level 2
        for (x, y) in coverage:
            self.levels[player][y][x] = 2

        # Step 3: mark all enemy stones currently in level>=1 as exposed (persisting)
        visible_enemy = {(x, y) for (x, y) in enemy_stones if self.levels[player][y][x] >= 1}
        self.exposed[player] |= visible_enemy
        # Drop exposures for stones that no longer exist
        self.exposed[player] &= enemy_stones

        # Step 4: force own stones and exposed enemy stones cells to level 2
        for (x, y) in own_stones:
            self.levels[player][y][x] = 2
        for (x, y) in self.exposed[player]:
            self.levels[player][y][x] = 2

    # ---- internals ----

    def _degrade(self, player: str):
        for y in range(self._szy):
            row = self.levels[player][y]
            for x in range(self._szx):
                if row[x] == 2:
                    row[x] = 1
                elif row[x] == 1:
                    row[x] = 0

    def _stones_state(self, player: str) -> Tuple[Set[Coord], Set[Coord], Set[Coord]]:
        """Return own stones, enemy stones, and occupied coords."""
        own: Set[Coord] = set()
        enemy: Set[Coord] = set()
        occupied: Set[Coord] = set()
        for m in self.game.stones:
            if m.player == player:
                own.add(m.coords)
            else:
                enemy.add(m.coords)
            occupied.add(m.coords)
        return own, enemy, occupied

    def _bfs_from_sources(
        self,
        sources: Set[Coord],
        max_steps: int,
        occupied: Set[Coord],
        block_paths: bool,
        include_sources: bool = False,
    ) -> Set[Coord]:
        """
        BFS over 4-neighbors up to `max_steps`.
        - If include_sources=True, also include the source cells themselves in the result; otherwise exclude them.
        - If block_paths=True: when encountering an occupied neighbor, include that neighbor but do not continue beyond it.
        - If block_paths=False: ignore blocking completely.
        """
        if not sources:
            return set()
        if max_steps <= 0:
            return set(sources) if include_sources else set()

        visited: Set[Coord] = set(sources)  # mark sources visited to avoid adding them
        result: Set[Coord] = set(sources) if include_sources else set()
        q: deque[Tuple[int, int, int]] = deque([(x, y, 0) for (x, y) in sources])

        def neighbors(x: int, y: int):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self._szx and 0 <= ny < self._szy:
                    yield nx, ny

        while q:
            x, y, d = q.popleft()
            if d >= max_steps:
                continue
            nd = d + 1
            for nx, ny in neighbors(x, y):
                if (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                result.add((nx, ny))
                if block_paths and (nx, ny) in occupied:
                    # include this cell but don't continue past it
                    continue
                # either not blocking, or ignoring blocks
                q.append((nx, ny, nd))
        return result

    def explore_around_point(self, coord: Coord, player: str, ignore_blocking: bool = True):
        """
        Explore around a specific point, optionally ignoring blocking stones.
        This is used when an illegal move is attempted to reveal the area.
        
        Args:
            coord: The coordinate to explore around
            player: The player who attempted the move
            ignore_blocking: If True, explore through stones; if False, stop at stones
        """
        if not (0 <= coord[0] < self._szx and 0 <= coord[1] < self._szy):
            return
        
        own_stones, enemy_stones, occupied = self._stones_state(player)
        
        # BFS from the attempted coord
        coverage = self._bfs_from_sources(
            {coord}, self.view_distance, occupied, 
            block_paths=not ignore_blocking, include_sources=True
        )
        
        # Mark explored cells as level 2
        for (x, y) in coverage:
            self.levels[player][y][x] = 2
        
        # Also mark own stones and exposed enemy stones
        for (x, y) in own_stones:
            self.levels[player][y][x] = 2
        for (x, y) in self.exposed[player]:
            self.levels[player][y][x] = 2
    
    def update_fog_view_snapshot(self):
        """
        Update the fog view snapshot. This method can be called after exploration
        to trigger any necessary UI updates or callbacks.
        
        Currently a placeholder for future extensibility - the actual snapshot
        is managed by KaTrainGui.fog_view_levels.
        """
        pass