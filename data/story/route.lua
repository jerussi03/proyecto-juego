-- Only implemented fighters launch a match. The other chapters are narrative.
local chapters = {
    {'chan', 'chan/chan.def'}, {'felix'}, {'alejandro'}, {'daniela'},
    {'hector', 'hector'}, {'gameros'}, {'armando'}, {'vladimir'},
    {'jaime'}, {'leonardo'}, {'victor'}, {'cesar'},
}
local function leave()
    setMatchNo(-1)
    start.exit = true
end
if matchNo() == 1 and not continued() then
    if not utcStory.show('intro') then leave(); return end
end
for i = math.max(1, matchNo()), #chapters do
    local chapter = chapters[i]
    if not continued() and not utcStory.show(chapter[1]) then leave(); return end
    if chapter[2] then
        if not launchFight{
            p1char = {'chava'}, p2char = {chapter[2]},
            p1numchars = 1, p2numchars = 1,
            p1teammode = 'single', p2teammode = 'single',
            stage = 'stages/patio.def', quickcontinue = true,
            winscreen = false, victoryscreen = false,
        } then return end
        if getWinnerTeam() ~= 1 then leave(); return end
    end
    if not utcStory.show(chapter[1]..'_after') then leave(); return end
    setMatchNo(i + 1)
end
utcStory.show('ending')
setMatchNo(-1)
