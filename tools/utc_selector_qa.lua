-- Isolated test module: render the expanded roster without changing controls.
local function run()
    main.f_default()
    getLastInputController = function() return 1 end
    for _, id in ipairs({'daniela', 'gameros', 'armando', 'vladimir', 'jaime', 'leonardo', 'cesar'}) do
        assert(main.t_charDef[id..'/'..id..'.def'] ~= nil, id..' missing from selector')
    end
    assert(motif.select_info.rows == 4 and motif.select_info.columns == 6)
    local callback = main.t_itemname.versus({{itemname = 'versus'}}, 1)
    local originalRefresh, tick = refresh, 0
    refresh = function()
        tick = tick + 1
        originalRefresh()
        if tick == 24 then screenshot() end
        if tick == 28 then
            local file = assert(io.open('scratch/utc-selector-result.txt', 'w'))
            file:write('PASS: seven new teachers registered; 4x6 selector rendered\n')
            file:close()
            os.exit()
        end
    end
    callback()
end
local originalStart = main.f_start
main.f_start = function(...)
    originalStart(...)
    main.menu.loop = run
end
