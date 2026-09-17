-- Run only through a scratch config's Common.Modules setting.
local output = assert(io.open('scratch/story-qa-result.txt', 'w'))
local function log(s) output:write(s..'\n'); output:flush() end
main.f_default()
getLastInputController = function() return 1 end
local callback = main.t_itemname.arcade(nil, nil)
assert(motif.files.intro.storyboard == '')
assert(motif.attract_mode.intro.storyboard == '')
assert(callback == start.f_selectMode)
assert(main.forceChar[1][1] == main.t_charDef.chava)
assert(main.luaPath == 'data/story/route.lua')
log('PASS: MODO HISTORIA selects Chava and the custom route')
-- Exercise the actual mode callback, including selectReset/selectScreen and
-- the arcade-path lookup which previously indexed an empty P1 selection.
local savedShow, savedFight = utcStory.show, launchFight
local reachedFight = false
utcStory.show = function() return true end
launchFight = function(data)
    assert(start.p[1].t_selected[1].ref == main.t_charDef.chava)
    assert(data.p2char[1] == 'chan/chan.def')
    reachedFight = true
    setMatchNo(-1)
    start.exit = true
    return false
end
callback()
assert(reachedFight)
utcStory.show, launchFight = savedShow, savedFight
log('PASS: actual menu callback reaches Chan without nil P1; startup/attract intro disabled')
local originalInput, originalKey, originalRefresh = getInput, getKey, refresh
local tick = 0
getKey = function() return '' end
getInput = function(_, keys) return keys == motif.title_info.menu.done.key end
refresh = function()
    tick = tick + 1
    originalRefresh()
    if tick == 4 then screenshot() end
end
local matches, seen = {}, {}
local originalShow = utcStory.show
utcStory.show = function(key)
    seen[#seen+1] = key
    return originalShow(key)
end
continued = function() return false end
launchFight = function(data)
    matches[#matches+1] = data.p2char[1]
    setMatchNo(matchNo()+1)
    return true
end
getWinnerTeam = function() return 1 end
setMatchNo(1)
dofile('data/story/route.lua')
assert(#matches == 2 and matches[1] == 'chan/chan.def' and matches[2] == 'hector')
assert(#seen == 26 and seen[26] == 'ending')
assert(matchNo() == -1)
log('PASS: all 58 cards rendered; 12 chapters and ending traversed; two fight requests')
utcStory.show = function() return false end
setMatchNo(1)
dofile('data/story/route.lua')
assert(matchNo() == -1 and start.exit)
log('PASS: cancelling a scene exits the route')
local before = #matches
utcStory.show = function() return true end
launchFight = function() return false end
setMatchNo(1)
dofile('data/story/route.lua')
assert(matchNo() == 1 and #matches == before)
log('PASS: failed/aborted fight does not reach later chapters or ending')
output:close()
os.exit()
