-- Integration smoke test: real mode callback, real fighter loading and match.
local function run()
local output = assert(io.open('scratch/story-fight-qa-result.txt', 'w'))
main.f_default()
getLastInputController = function() return 1 end
local callback = main.t_itemname.arcade(nil, nil)
main.cpuSide[1] = true
main.motif.hiscore = false
local scenes = {}
utcStory.show = function(key) scenes[#scenes+1] = key; return true end
local fight = launchFight
local reached = false
launchFight = function(data)
    assert(start.p[1].t_selected[1].ref == main.t_charDef.chava)
    assert(scenes[1] == 'intro' and scenes[2] == 'chan')
    data.time = 1
    data.p1rounds, data.p2rounds = 1, 1
    data.continue = false
    data.vsscreen = false
    data.ai = 8
    output:write('Reached real Chava vs Chan loading from menu callback\n'); output:flush()
    fight(data)
    reached = true
    output:write('PASS: real match completed; winner team '..getWinnerTeam()..'\n'); output:flush()
    setMatchNo(-1)
    start.exit = true
    return false
end
callback()
assert(reached)
output:write('PASS: returned from campaign without error\n')
output:close()
os.exit()
end
local startMenu = main.f_start
main.f_start = function(...)
    startMenu(...)
    main.menu.loop = run
end
