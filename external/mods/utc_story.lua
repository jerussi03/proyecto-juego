-- Illustrated story reader. Portraits and text are packaged locally in an SFF.
utcStory = {pages = dofile('data/story/pages.lua')}

function utcStory.show(key)
    if not utcStory.sff then utcStory.sff = sffNew('data/story/story.sff') end
    local pages = assert(utcStory.pages[key], 'Missing story chapter: '..key)
    local page, age, animation = 1, 0, nil
    resetKey()
    esc(false)
    while true do
        if not animation then
            animation = animNew(utcStory.sff, '0,'..pages[page]..',0,0,-1')
            animSetLocalcoord(animation, 1280, 720)
            animSetPos(animation, 0, 0)
            animSetScale(animation, 1, 1)
            age = 0
        end
        if esc() then
            esc(false)
            resetKey()
            resetTokenGuard()
            return false
        end
        local nextPage = getInput(-1, motif.title_info.menu.done.key) or getKey() == 'RETURN'
        local previous = getInput(-1, {'L'})
        if age > 12 and (nextPage or previous) then
            resetKey()
            if previous then
                page = math.max(1, page - 1)
            else
                page = page + 1
            end
            if page > #pages then
                resetTokenGuard()
                return true
            end
            animation = nil
        else
            clearColor(16,25,32)
            animUpdate(animation)
            animDraw(animation)
            refresh()
            age = age + 1
        end
    end
end

-- Skipping character selection also skips the engine's forceChar handling.
-- Populate Chava after each reset, before the arcade-path lookup reads P1.ref.
hook.add('start.f_selectReset.side', 'utc_story_chava', function(side, hardReset, preserveProgress, p)
    if side ~= 1 or main.luaPath ~= 'data/story/route.lua' then return end
    p.t_selected = {{ref = assert(main.t_charDef.chava), pal = 1, pn = 1}}
    p.numChars = 1
    p.teamMode = 0
    p.teamEnd = true
    p.selEnd = true
end)

-- The existing MODO HISTORIA button starts Chava's campaign.
local arcade = main.t_itemname.arcade
main.t_itemname.arcade = function(t, item)
    local result = arcade(t, item)
    main.forceChar[1] = {assert(main.t_charDef['chava'])}
    main.selectMenu[1] = false
    main.luaPath = 'data/story/route.lua'
    main.storyboard.credits = false
    main.storyboard.gameover = false
    main.storyboard.ending = false
    main.motif.winscreen = false
    return result
end
