package org.libsdl.app;

// Modified from ikemen-droid for verified, versioned game content installation.
import android.content.res.AssetManager;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import org.json.JSONArray;
import org.json.JSONObject;

public final class AssetExtractor {
    private static final String VERSION = "content-version.txt";
    private static final String MARKER = ".utc-content-version";
    public interface Progress { void changed(int complete, int total); }

    private static String readAsset(AssetManager assets, String path) throws IOException {
        try (InputStream in = assets.open(path)) {
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
    }
    private static JSONArray manifest(AssetManager assets) throws IOException {
        try {
            JSONArray entries = new JSONObject(readAsset(assets, "asset-manifest.json")).getJSONArray("files");
            if (entries.length() == 0) throw new IOException("El manifiesto del juego está vacío.");
            return entries;
        } catch (org.json.JSONException error) { throw new IOException("Manifiesto del juego no válido.", error); }
    }
    private static String version(AssetManager assets) throws IOException {
        String value = readAsset(assets, VERSION).trim();
        if (value.isEmpty()) throw new IOException("Falta la versión del juego.");
        return value;
    }
    private static File destination(File root, String relative) throws IOException {
        if (relative.startsWith("/") || relative.contains("\\")) throw new IOException("Ruta no válida: " + relative);
        File file = new File(root, relative).getCanonicalFile();
        if (!file.getPath().startsWith(root.getCanonicalPath() + File.separator)) {
            throw new IOException("Ruta fuera del juego: " + relative);
        }
        return file;
    }
    public static boolean needsUpdate(AssetManager assets, File root) throws IOException {
        File marker = new File(root, MARKER);
        if (!marker.isFile() || !new String(Files.readAllBytes(marker.toPath()), StandardCharsets.UTF_8).trim().equals(version(assets))) return true;
        JSONArray entries = manifest(assets);
        try {
            for (int i=0; i<entries.length(); i++) {
                if (!destination(root, entries.getJSONObject(i).getString("path")).isFile()) return true;
            }
        } catch (org.json.JSONException error) { throw new IOException("Manifiesto incompleto.", error); }
        return false;
    }
    public static void extractAll(AssetManager assets, File root, Progress progress) throws IOException {
        JSONArray entries = manifest(assets);
        String expectedVersion = version(assets);
        if (!root.isDirectory() && !root.mkdirs()) throw new IOException("No se pudo crear la carpeta del juego.");
        byte[] buffer = new byte[65536];
        try {
            for (int i=0; i<entries.length(); i++) {
                JSONObject entry = entries.getJSONObject(i);
                String relative = entry.getString("path");
                File file = destination(root, relative);
                // Preserve existing saves and player settings when updating the APK.
                if (!(relative.startsWith("save/") && file.isFile())) {
                    File parent = file.getParentFile();
                    if (!parent.isDirectory() && !parent.mkdirs()) throw new IOException("No se pudo crear " + relative);
                    File staging = new File(parent, file.getName() + ".utc-new");
                    MessageDigest digest = MessageDigest.getInstance("SHA-256");
                    long count=0;
                    try (InputStream in = assets.open(relative); FileOutputStream out = new FileOutputStream(staging)) {
                        int read;
                        while ((read=in.read(buffer)) != -1) {
                            out.write(buffer,0,read); digest.update(buffer,0,read); count+=read;
                        }
                        out.getFD().sync();
                    } catch (IOException failure) {
                        staging.delete(); throw new IOException("No se pudo instalar " + relative, failure);
                    }
                    StringBuilder hex = new StringBuilder();
                    for (byte value : digest.digest()) hex.append(String.format(java.util.Locale.ROOT,"%02x",value & 255));
                    if (count != entry.getLong("bytes") || !hex.toString().equalsIgnoreCase(entry.getString("sha256"))) {
                        staging.delete(); throw new IOException("Archivo del juego dañado: " + relative);
                    }
                    Files.move(staging.toPath(), file.toPath(), StandardCopyOption.REPLACE_EXISTING);
                }
                if ((i+1)%8 == 0 || i+1 == entries.length()) progress.changed(i+1,entries.length());
            }
            Files.write(new File(root,MARKER).toPath(),expectedVersion.getBytes(StandardCharsets.UTF_8));
        } catch (org.json.JSONException | java.security.NoSuchAlgorithmException error) {
            throw new IOException("No se pudo verificar el contenido del juego.",error);
        }
    }
}
