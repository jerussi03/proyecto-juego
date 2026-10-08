-- All professors fight; the project rehearsal is a narrative interlude.
local chapters = {
    {'chan', 'chan_kof/chan_kof.def'}, {'felix', 'felix/felix.def'}, {'alejandro', 'alejandro/alejandro.def'}, {'daniela', 'daniela/daniela.def'},
    {'hector', 'hector'}, {'gameros', 'gameros/gameros.def'}, {'armando', 'armando/armando.def'}, {'vladimir', 'vladimir/vladimir.def'},
    {'jaime', 'jaime/jaime.def'}, {'leonardo', 'leonardo/leonardo.def'}, {'proyecto'}, {'cesar', 'cesar/cesar.def'},
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
