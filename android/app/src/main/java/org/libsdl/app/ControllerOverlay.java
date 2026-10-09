package org.libsdl.app;

// Original The King of UTc touch layout; input uses the upstream SDL bridge.
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowInsets;
import java.util.*;

public final class ControllerOverlay extends View {
    private static final int DEVICE_ID = 0x555443;
    private static final int A=KeyEvent.KEYCODE_BUTTON_A, B=KeyEvent.KEYCODE_BUTTON_B;
    private static final int C=KeyEvent.KEYCODE_BUTTON_X, D=KeyEvent.KEYCODE_BUTTON_Y;
    private static final int ESCAPE=-KeyEvent.KEYCODE_ESCAPE;
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final List<TouchButton> buttons=new ArrayList<>();
    private final Set<Integer> held=new HashSet<>();
    private float dpadX,dpadY,dpadRadius,unit;
    private int hatX,hatY,insetLeft,insetRight;
    private boolean initialized, menuGesture;

    private static final class TouchButton {
        final String label,subtitle;
        final RectF bounds;
        final int[] codes;
        final int color;
        final boolean circular;
        TouchButton(String label,String subtitle,RectF bounds,int color,boolean circular,int... codes) {
            this.label=label; this.subtitle=subtitle; this.bounds=bounds;
            this.color=color; this.circular=circular; this.codes=codes;
        }
        boolean contains(float x,float y) {
            if (!circular) return bounds.contains(x,y);
            float dx=x-bounds.centerX(),dy=y-bounds.centerY(),r=bounds.width()/2;
            return dx*dx+dy*dy <= r*r;
        }
    }
    public ControllerOverlay(Context context) {
        super(context);
        setContentDescription("Cruceta, A puño, B patada, C puño fuerte, D patada fuerte, esquiva, MAX y pausa");
        setClickable(true); setFocusable(false); setKeepScreenOn(true);
    }
    private float dp(float value) { return value*getResources().getDisplayMetrics().density; }
    @Override public WindowInsets onApplyWindowInsets(WindowInsets insets) {
        android.graphics.Insets safe=insets.getInsets(WindowInsets.Type.displayCutout());
        insetLeft=safe.left; insetRight=safe.right;
        rebuild(getWidth(),getHeight());
        return super.onApplyWindowInsets(insets);
    }
    @Override protected void onSizeChanged(int w,int h,int oldW,int oldH) { releaseAll(); rebuild(w,h); }
    private void rebuild(int w,int h) {
        buttons.clear();
        if (w<=0 || h<=0) return;
        float left=insetLeft,right=w-insetRight;
        unit=Math.min(dp(65),Math.min(h*.17f,(right-left)*.078f));
        dpadRadius=Math.min(dp(90),Math.min(h*.24f,(right-left)*.15f));
        dpadX=left+dpadRadius+dp(20); dpadY=h-dpadRadius-dp(24);
        circle("A","PUÑO",right-unit*3.35f,h-unit*1.05f,0xff42d7c4,A);
        circle("B","PATADA",right-unit*2.15f,h-unit*.8f,0xff65b8ff,B);
        circle("C","PUÑO +",right-unit*2.8f,h-unit*2.3f,0xffffcb68,C);
        circle("D","PATADA +",right-unit*1.55f,h-unit*2.0f,0xffef7ea6,D);
        float comboY=h-unit*3.8f;
        pill("AB","ESQUIVA",right-unit*4.0f,comboY,unit*1.15f,A,B);
        pill("BC","MAX",right-unit*2.7f,comboY,unit*1.15f,B,C);
        pill("CD","FUERTE",right-unit*1.4f,comboY,unit*1.15f,C,D);
        float width=Math.min(dp(90),(right-left)*.12f),top=dp(29);
        pill("ATRÁS","",left+dp(12)+width/2,top,width,ESCAPE);
        pill("PAUSA","",right-width*1.7f-dp(18),top,width,KeyEvent.KEYCODE_BUTTON_SELECT);
        pill("START","",right-width/2-dp(12),top,width,KeyEvent.KEYCODE_BUTTON_START);
        invalidate();
    }
    private void circle(String label,String subtitle,float x,float y,int color,int code) {
        float r=unit*.48f;
        buttons.add(new TouchButton(label,subtitle,new RectF(x-r,y-r,x+r,y+r),color,true,code));
    }
    private void pill(String label,String subtitle,float x,float y,float width,int... codes) {
        float halfHeight=dp(subtitle.isEmpty()?17:22);
        buttons.add(new TouchButton(label,subtitle,new RectF(x-width/2,y-halfHeight,x+width/2,y+halfHeight),0xffb7c9de,false,codes));
    }
    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        paint.setStyle(Paint.Style.FILL); paint.setColor(0xa621344e);
        canvas.drawCircle(dpadX,dpadY,dpadRadius,paint);
        paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(dp(2)); paint.setColor(0xaa8fc4de);
        canvas.drawCircle(dpadX,dpadY,dpadRadius,paint);
        paint.setStyle(Paint.Style.FILL);
        float mark=dpadRadius*.65f;
        direction(canvas,"↑",dpadX,dpadY-mark,hatY<0); direction(canvas,"↓",dpadX,dpadY+mark,hatY>0);
        direction(canvas,"←",dpadX-mark,dpadY,hatX<0); direction(canvas,"→",dpadX+mark,dpadY,hatX>0);
        paint.setColor(0x779fbdcf); canvas.drawCircle(dpadX,dpadY,dpadRadius*.13f,paint);
        for (TouchButton button:buttons) {
            boolean pressed=true;
            for (int code:button.codes) pressed &= held.contains(code);
            paint.setColor(pressed?0xdd34546a:0xa916283d); paint.setStyle(Paint.Style.FILL);
            shape(canvas,button);
            paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(dp(pressed?3:1.5f)); paint.setColor(button.color);
            shape(canvas,button);
            paint.setStyle(Paint.Style.FILL); paint.setTextAlign(Paint.Align.CENTER);
            paint.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
            paint.setTextSize(button.circular?unit*.35f:dp(13));
            float labelY=button.bounds.centerY()+dp(button.subtitle.isEmpty()?4:-1);
            canvas.drawText(button.label,button.bounds.centerX(),labelY,paint);
            if (!button.subtitle.isEmpty()) {
                paint.setColor(Color.WHITE); paint.setTextSize(dp(button.circular?8:8.5f));
                canvas.drawText(button.subtitle,button.bounds.centerX(),labelY+dp(12),paint);
            }
        }
    }
    private void shape(Canvas canvas,TouchButton button) {
        if (button.circular) canvas.drawOval(button.bounds,paint);
        else canvas.drawRoundRect(button.bounds,dp(12),dp(12),paint);
    }
    private void direction(Canvas canvas,String label,float x,float y,boolean pressed) {
        paint.setColor(pressed?0xff42d7c4:0xbbffffff); paint.setTextSize(dpadRadius*.36f); paint.setTextAlign(Paint.Align.CENTER);
        canvas.drawText(label,x,y+dpadRadius*.12f,paint);
    }
    public void initializeVirtualController() {
        if (initialized) return;
        SDLControllerManager.nativeAddJoystick(DEVICE_ID,"Xbox 360 Controller","UTC Touch",0x045e,0x028e,false,0xfff,6,0x3f,1,0);
        initialized=true;
        SDLControllerManager.onNativeHat(DEVICE_ID,0,0,0);
    }
    @Override public boolean onTouchEvent(MotionEvent event) {
        if (event.getActionMasked()==MotionEvent.ACTION_CANCEL) { releaseAll(); return true; }
        initializeVirtualController();
        int action=event.getActionMasked(),nextHatX=0,nextHatY=0;
        boolean directionFound=false;
        Set<Integer> nextHeld=new HashSet<>();
        for (int i=0;i<event.getPointerCount();i++) {
            if (action==MotionEvent.ACTION_UP || (action==MotionEvent.ACTION_POINTER_UP && i==event.getActionIndex())) continue;
            float x=event.getX(i),y=event.getY(i);
            boolean overButton=false;
            for (TouchButton button:buttons) {
                if (button.contains(x,y)) { overButton=true; for (int code:button.codes) nextHeld.add(code); }
            }
            float dx=x-dpadX,dy=y-dpadY,distance=(float)Math.hypot(dx,dy);
            if (!directionFound && !overButton && distance<dpadRadius*1.25f) {
                directionFound=true;
                if (distance>dpadRadius*.20f) {
                    int octant=Math.floorMod((int)Math.floor((Math.atan2(dy,dx)+Math.PI/8)/(Math.PI/4)),8);
                    int[] xs={1,1,0,-1,-1,-1,0,1},ys={0,1,1,1,0,-1,-1,-1};
                    nextHatX=xs[octant]; nextHatY=ys[octant];
                }
            }
        }
        int menu=KeyEvent.KEYCODE_BUTTON_SELECT;
        if ((nextHeld.contains(menu) && !held.contains(menu)) ||
                (nextHeld.contains(ESCAPE) && !held.contains(ESCAPE))) menuGesture=true;
        if (menuGesture) {
            nextHeld.removeIf(code -> code!=menu && code!=ESCAPE);
            nextHatX=0; nextHatY=0;
        }
        // Union keeps buttons down while any finger or combination still holds them.
        for (int code:held) if (!nextHeld.contains(code)) emit(code,false);
        for (int code:nextHeld) if (!held.contains(code)) emit(code,true);
        held.clear(); held.addAll(nextHeld);
        if (nextHatX!=hatX || nextHatY!=hatY) {
            hatX=nextHatX; hatY=nextHatY; SDLControllerManager.onNativeHat(DEVICE_ID,0,hatX,hatY);
        }
        if (action==MotionEvent.ACTION_UP) { menuGesture=false; performClick(); }
        invalidate(); return true;
    }
    private void emit(int code,boolean down) {
        if (code==ESCAPE) {
            if (down) SDLActivity.onNativeKeyDown(KeyEvent.KEYCODE_ESCAPE);
            else SDLActivity.onNativeKeyUp(KeyEvent.KEYCODE_ESCAPE);
        } else if (down) SDLControllerManager.onNativePadDown(DEVICE_ID,code);
        else SDLControllerManager.onNativePadUp(DEVICE_ID,code);
    }
    public void releaseAll() {
        for (int code:held) emit(code,false);
        held.clear();
        if (initialized) SDLControllerManager.onNativeHat(DEVICE_ID,0,0,0);
        hatX=0; hatY=0; menuGesture=false; invalidate();
    }
    @Override public boolean performClick() { super.performClick(); return true; }
    @Override protected void onDetachedFromWindow() { releaseAll(); super.onDetachedFromWindow(); }
}
