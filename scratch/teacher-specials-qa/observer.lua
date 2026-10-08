
if player(1) and roundState() == 2 then
  local t = var(58)
  if t > 0 and t ~= teacherLastTick then
    teacherLastTick = t
    local values = {t, stateNo(), time(), power(), life(), 0, var(40), var(46), var(48), numHelper(1005), numHelper(3010), numHelper(1006), numHelper(8200), fvar(29), fvar(30), fvar(31), posX(), facing(), fvar(32), fvar(33), numHelper(8219), fvar(35), fvar(34), fvar(36), var(44), var(45), posY(), numHelper(1050), 0}
    if teacherQAID == "daniela" and (t == 120 or t == 260 or t == 1550 or t == 1590 or t == 1630) then screenshot() end
    local signature = {chan_kof=1010, felix=1010, alejandro=1040, daniela=1010, gameros=1040, armando=1040, vladimir=1000, jaime=1000, leonardo=1000, cesar=1000}
    teacherCaptured = teacherCaptured or {}
    if stateNo() == signature[teacherQAID] and time() >= 18 and not teacherCaptured[teacherQAID] then
      teacherCaptured[teacherQAID] = true
      screenshot()
    end
    if enemyNear() then values[6] = life(); values[29] = power() end
    player(1)
    local f = assert(io.open("scratch/teacher-specials-qa/" .. teacherQAID .. ".csv", "a"))
    f:write(table.concat(values, ",") .. "\n")
    f:close()
    if t >= 9600 then os.exit() end
  end
end
