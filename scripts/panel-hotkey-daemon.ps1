$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class JetspaceHotkeyContext : ApplicationContext {
    [DllImport("user32.dll")]
    private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);
    [DllImport("user32.dll")]
    private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

    private const int WM_HOTKEY = 0x0312;
    private const uint MOD_ALT = 0x0001;
    private const uint MOD_CONTROL = 0x0002;
    private const uint MOD_NOREPEAT = 0x4000;
    private const uint VK_J = 0x4A;
    private const int HOTKEY_ID = 7001;

    private readonly NotifyIcon _tray;
    private readonly MessageWindow _window;
    private readonly string _url;

    public JetspaceHotkeyContext(string url) {
        _url = url;
        _window = new MessageWindow(this);
        _tray = new NotifyIcon {
            Icon = System.Drawing.SystemIcons.Information,
            Visible = true,
            Text = "Jetspace Control Panel (Ctrl+Alt+J)"
        };
        var menu = new ContextMenuStrip();
        menu.Items.Add("Open Control Panel", null, (s,e) => OpenPanel());
        menu.Items.Add("Exit", null, (s,e) => ExitThread());
        _tray.ContextMenuStrip = menu;
        _tray.DoubleClick += (s,e) => OpenPanel();

        if (!RegisterHotKey(_window.Handle, HOTKEY_ID, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_J)) {
            throw new Exception("Failed to register Ctrl+Alt+J.");
        }
    }

    public void OpenPanel() {
        Process.Start(new ProcessStartInfo { FileName = _url, UseShellExecute = true });
    }

    protected override void ExitThreadCore() {
        UnregisterHotKey(_window.Handle, HOTKEY_ID);
        _tray.Visible = false;
        _tray.Dispose();
        _window.DestroyHandle();
        base.ExitThreadCore();
    }

    private class MessageWindow : NativeWindow {
        private readonly JetspaceHotkeyContext _ctx;
        public MessageWindow(JetspaceHotkeyContext ctx) {
            _ctx = ctx;
            CreateHandle(new CreateParams());
        }
        protected override void WndProc(ref Message m) {
            if (m.Msg == WM_HOTKEY && m.WParam.ToInt32() == HOTKEY_ID) {
                _ctx.OpenPanel();
            }
            base.WndProc(ref m);
        }
    }
}
"@

Add-Type -TypeDefinition $code -ReferencedAssemblies System.Windows.Forms,System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
[System.Windows.Forms.Application]::Run([JetspaceHotkeyContext]::new("http://127.0.0.1:8010/control"))
