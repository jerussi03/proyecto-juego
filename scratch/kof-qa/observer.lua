
if player(1) then
  local t = var(58)
  if t > 0 and t ~= kofLastTick then
    kofLastTick = t
    local f = assert(io.open("scratch/kof-qa/" .. name() .. "-input.csv", "a"))
    f:write(string.format("%d,%d,%d,%d,%d,%d,%d,%f,%f\n",t,stateNo(),anim(),time(),power(),var(40),numExplod(9900),posX(),velX()))
    f:close()
    if (stateNo() == 900 and time() == 5) or (stateNo() == 400 and animElemNo(0) == 4 and animElemTime(4) == 0) then screenshot() end
    if t >= 5600 then os.exit() end
  end
end
