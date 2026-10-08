-- Debug loop for an isolated Daniela match, loaded only by a scratch config.
if player(1) and name() == 'Daniela' and roundState() == 2 then
    utcCompanionTick = (utcCompanionTick or 0) + 1
    if utcCompanionTick == 120 then
        assert(numHelper(8200) == 1, 'Victor companion was not spawned exactly once')
        local file = assert(io.open('scratch/utc-companion-result.txt', 'w'))
        file:write('PASS: Daniela has exactly one Victor companion during the fight\n')
        file:close()
        screenshot()
    end
end
